import os
import sys
import argparse
import time
import random
import uuid
import importlib.util
import concurrent.futures
import google.generativeai as genai

# ─────────────────────────────────────────────────
# CONSTANTS & SETUP
# ─────────────────────────────────────────────────
MODULE_KEYS = ["01_DSA", "02_Data_Science_ML", "03_LLD", "04_HLD"]
MODEL_NAME = "models/gemma-4-31b-it"

# ─────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────
def load_api_key():
    api_key = os.environ.get("API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key and os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return api_key

def load_info(info_path):
    """Dynamically load INFO dict from info.py without cache collision."""
    try:
        module_name = f"info_{uuid.uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, info_path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)
        info = getattr(mod, "INFO", None)
        sys.modules.pop(module_name, None)
        return info
    except Exception as e:
        print(f"Error loading {info_path}: {e}")
        return None

def is_placeholder(info, challenge_key):
    is_design = info.get("type") == "design" or challenge_key.endswith(".md")
    sol = info.get("solutions", "")
    if not sol:
        return True
    sol_lower = sol.lower()
    if is_design:
        if "detailed system components" in sol_lower or len(sol.strip()) < 150:
            return True
    else:
        if "# ..." in sol or "pass" in sol_lower or len(sol.strip()) < 150:
            return True
        if not sol.strip().startswith("# --- APPROACH 1:"):
            return True
    return False

def extract_function_name(starter_code):
    if not starter_code:
        return "solve"
    for line in starter_code.split("\n"):
        line = line.strip()
        if line.startswith("def "):
            return line.split("def ", 1)[1].split("(", 1)[0].strip()
        elif line.startswith("class "):
            return line.split("class ", 1)[1].split(":", 1)[0].split("(", 1)[0].strip()
    return "solve"

def get_java_class_name(challenge_key):
    name = challenge_key
    if "_" in name and (name[:2].isdigit() or (name.startswith("q") and name[1:3].isdigit())):
        name = name.split("_", 1)[1]
    parts = name.split("_")
    return "".join(part.capitalize() for part in parts)

def serialize_info(info):
    output = "INFO = {\n"
    for k, v in info.items():
        key_str = f"    {repr(k)}: "
        if isinstance(v, str):
            if "\n" in v:
                escaped = v.replace('"""', '\\"\\"\\"')
                val_str = f'"""{escaped}"""'
            else:
                val_str = repr(v)
        else:
            val_str = repr(v)
        output += f"{key_str}{val_str},\n"
    output += "}\n"
    return output

def update_physical_py_file(code_path, new_solutions):
    if not os.path.exists(code_path):
        return False
    try:
        with open(code_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        marker = "# ====================================================================="
        idx = content.find(marker)
        if idx != -1:
            header_block = (
                "# =====================================================================\n"
                "# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS\n"
                "# =====================================================================\n"
            )
            new_content = content[:idx] + header_block + "\n" + new_solutions + "\n"
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error updating py file {code_path}: {e}")
    return False

def update_physical_md_file(challenge_dir, challenge_key, new_solutions):
    if not os.path.exists(challenge_dir):
        return False
    try:
        sol_path = os.path.join(challenge_dir, f"{challenge_key}_solution.md")
        with open(sol_path, "w", encoding="utf-8") as f:
            f.write(new_solutions)
        return True
    except Exception as e:
        print(f"Error updating md file in {challenge_dir}: {e}")
    return False

# ─────────────────────────────────────────────────
# API CALL HANDLING
# ─────────────────────────────────────────────────
def generate_solution_api(challenge):
    info = challenge["info"]
    challenge_key = challenge["challenge_key"]
    topic_key = challenge["topic_key"]
    module_key = challenge["module_key"]
    
    is_design = info.get("type") == "design" or challenge_key.endswith(".md")
    
    if is_design:
        prompt = f"""You are a Staff Systems Architect.
You are given a system design or low-level design challenge:
Module: {module_key}
Topic: {topic_key}
Challenge: {challenge_key}
Difficulty: {info.get('difficulty', 'Medium')}
Description: {info.get('description', '')}

Please write a comprehensive, high-quality, and professional-grade solution guide for this design challenge in Markdown.
The solution guide should include:
1. Requirements & System Constraints (Functional & Non-Functional, Scale Estimations if HLD).
2. High-Level Architecture (Core components, their interactions, and a text-based ASCII or Mermaid sequence/architecture diagram).
3. Detailed Database Schema Design (Tables, fields, primary/foreign keys, index selections, NoSQL vs SQL reasoning).
4. Core API Design (HTTP endpoints, request/response payloads in JSON).
5. Scalability & Advanced Topics (Caching strategies, load balancing, sharding/partitioning, message queues, rate limiting, and fault tolerance).
6. Trade-off Analysis (CAP theorem priorities, latency vs storage, etc.).

Return ONLY the raw Markdown content. Do NOT wrap it in extra markdown code block formatting (like ```markdown or ```) at the root level, and do NOT write any conversational intro or outro.
"""
    else:
        func_name = extract_function_name(info.get("starter_code", ""))
        java_class = get_java_class_name(challenge_key)
        prompt = f"""You are an elite Software Engineer and Algorithm Specialist.
You are given a coding challenge definition:
Module: {module_key}
Topic: {topic_key}
Challenge: {challenge_key}
Difficulty: {info.get('difficulty', 'Medium')}
Description: {info.get('description', '')}
Starter Code:
{info.get('starter_code', '')}

Please generate a complete, production-grade, and correct solutions file for this challenge in Python.
You must provide exactly three approaches matching the following format:
1. Approach 1: A brute-force / naive / alternative approach in Python. Include Time Complexity and Space Complexity.
2. Approach 2: The optimal Python approach. Include Time Complexity and Space Complexity. Explain why it is optimal.
3. Approach 3: A Java variant of the optimal solution wrapped inside a multi-line string comment.

The format of the returned content MUST be exactly like this:
# --- APPROACH 1: Naive (Brute Force) ---
# Time Complexity: O(...)
# Space Complexity: O(...)
# [Short explanation]
def {func_name}_naive(...):
    # Implementation

# --- APPROACH 2: Optimal ([Algorithm/Data Structure used]) ---
# Time Complexity: O(...)
# Space Complexity: O(...)
# [Short explanation]
def {func_name}_optimal(...):
    # Implementation

# --- APPROACH 3: Secondary Language (Java Variant) ---
\"\"\"
package {topic_key};

import ...;

public class {java_class} {{
    // Java implementation
}}
\"\"\"

Guidelines:
1. Ensure the signatures of the Python functions match the parameter names and types from the starter code.
2. Ensure the code is 100% correct, syntactically valid, and handles edge cases.
3. Return ONLY the raw Python code. Do NOT wrap it in markdown block formatting (like ```python or ```) and do NOT write any conversational text before or after the code.
"""

    retries = 5
    backoff = 5.0
    while retries > 0:
        try:
            model = genai.GenerativeModel(MODEL_NAME)
            response = model.generate_content(prompt)
            
            # Extract content from candidate parts
            parts = []
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, "text") and part.text:
                                parts.append(part.text)
            text = "".join(parts).strip()
            
            if text:
                # Clean up wrapping markdown block formatting if model ignored the instruction
                if text.startswith("```"):
                    lines = text.split("\n")
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines[-1].startswith("```"):
                        lines = lines[:-1]
                    text = "\n".join(lines).strip()
                
                # Strip out any model-generated chain-of-thought/planning prefix
                if is_design:
                    idx = text.find("# ")
                    if idx != -1:
                        text = text[idx:]
                else:
                    idx = text.find("# --- APPROACH 1:")
                    if idx != -1:
                        text = text[idx:]
                        
                return text
            else:
                raise Exception("Empty response from model.")
        except Exception as e:
            err_str = str(e)
            print(f"[{challenge_key}] API Error: {err_str}")
            if "429" in err_str or "resource exhausted" in err_str.lower() or "quota" in err_str.lower():
                sleep_time = backoff + random.uniform(1.0, 3.0)
                print(f"[{challenge_key}] Rate limit hit. Retrying in {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                backoff *= 2
                retries -= 1
            else:
                time.sleep(2.0)
                retries -= 1
                
    raise Exception(f"Failed to generate solution for {challenge_key} after multiple retries.")

# ─────────────────────────────────────────────────
# CORE PROCESSOR
# ─────────────────────────────────────────────────
def process_challenge(challenge, dry_run=False):
    challenge_key = challenge["challenge_key"]
    info_path = challenge["info_path"]
    
    print(f"[PENDING] Processing [{challenge_key}]...")
    if dry_run:
        print(f"[INFO] [Dry-Run] Placeholder identified for [{challenge_key}].")
        return True
        
    try:
        sol_text = generate_solution_api(challenge)
        
        # 1. Update info.py dict
        info = challenge["info"]
        info["solutions"] = sol_text
        serialized = serialize_info(info)
        with open(info_path, "w", encoding="utf-8") as f:
            f.write(serialized)
        
        # 2. Update physical code/design files if initialized
        challenge_dir = os.path.dirname(info_path)
        is_design = info.get("type") == "design" or challenge_key.endswith(".md")
        
        if is_design:
            updated_physical = update_physical_md_file(challenge_dir, challenge_key, sol_text)
        else:
            code_path = os.path.join(challenge_dir, f"{challenge_key}.py")
            updated_physical = update_physical_py_file(code_path, sol_text)
            
        status = "and physical files updated" if updated_physical else "(not physically initialized yet)"
        print(f"[SUCCESS] [{challenge_key}] Solution successfully updated in metadata {status}!")
        return True
    except Exception as e:
        print(f"[ERROR] [{challenge_key}] Failed: {e}")
        return False

# ─────────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Bulk solution generator script using Gemma 4 31B.")
    parser.add_argument("--dry-run", action="store_true", help="Find and list stubs/placeholders without querying API.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of generated solutions.")
    parser.add_argument("--challenge", type=str, default=None, help="Process a single specific challenge by key.")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("Error: API_KEY or GEMINI_API_KEY environment variable is not set and .env file is missing.")
        sys.exit(1)
        
    genai.configure(api_key=api_key)

    # Walk directory to collect all info.py metadata
    all_challenges = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for module in MODULE_KEYS:
        module_path = os.path.join(base_dir, module)
        if not os.path.exists(module_path):
            continue
        for topic in os.listdir(module_path):
            topic_path = os.path.join(module_path, topic)
            if not os.path.isdir(topic_path) or topic.startswith(".") or topic == "__pycache__":
                continue
            for challenge in os.listdir(topic_path):
                challenge_path = os.path.join(topic_path, challenge)
                if not os.path.isdir(challenge_path) or not challenge.startswith("q") or challenge == "__pycache__":
                    continue
                info_path = os.path.join(challenge_path, "info.py")
                if os.path.exists(info_path):
                    info = load_info(info_path)
                    if info:
                        all_challenges.append({
                            "module_key": module,
                            "topic_key": topic,
                            "challenge_key": challenge,
                            "info_path": info_path,
                            "info": info
                        })

    print(f"[SCAN] Scanned {len(all_challenges)} challenges in the repository.")
    
    # Filter to placeholders
    placeholders = []
    for c in all_challenges:
        if args.challenge and c["challenge_key"] != args.challenge:
            continue
        if is_placeholder(c["info"], c["challenge_key"]):
            placeholders.append(c)
            
    print(f"[LIST] Found {len(placeholders)} challenges with placeholder solutions.")
    
    if args.dry_run:
        print("\nList of identified placeholder challenges:")
        for idx, p in enumerate(placeholders):
            print(f"  {idx+1}. [{p['module_key']}/{p['topic_key']}/{p['challenge_key']}]")
        return

    if not placeholders:
        print("No placeholder solutions found! Everything is up to date.")
        return

    # Apply limits
    if args.limit is not None:
        placeholders = placeholders[:args.limit]
        print(f"[WARNING] Limit applied: only generating solutions for first {len(placeholders)} challenges.")

    # Execute in parallel with 3 workers
    print(f"[START] Starting generation using {MODEL_NAME} with max 3 concurrent requests...")
    
    start_time = time.time()
    success_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Submit all tasks
        futures = {executor.submit(process_challenge, p, dry_run=False): p for p in placeholders}
        
        # Gather results
        for future in concurrent.futures.as_completed(futures):
            challenge = futures[future]
            try:
                result = future.result()
                if result:
                    success_count += 1
            except Exception as e:
                print(f"Fatal error processing {challenge['challenge_key']}: {e}")

    elapsed = time.time() - start_time
    print(f"\n[SUMMARY] Solution Update Complete!")
    print(f"Successfully updated: {success_count}/{len(placeholders)} challenges.")
    print(f"Total time elapsed: {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
