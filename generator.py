import os
import re
from questions_db import CHALLENGES_DB

def extract_function_name(starter_code):
    if not starter_code:
        return "solve"
    for line in starter_code.split("\n"):
        line = line.strip()
        if line.startswith("def "):
            # Extract func name: def function_name(...)
            return line.split("def ", 1)[1].split("(", 1)[0].strip()
        elif line.startswith("class "):
            # Extract class name: class ClassName(...)
            return line.split("class ", 1)[1].split(":", 1)[0].split("(", 1)[0].strip()
    return "solve"

def initialize_challenge(module_key, topic_key, challenge_key):
    """
    Dynamically generates the directory and target files (code, tests, readme)
    for a selected challenge based on the questions_db definition.
    """
    if module_key not in CHALLENGES_DB or topic_key not in CHALLENGES_DB[module_key]:
        return False, "Module or Topic not found in catalog."
        
    topic_db = CHALLENGES_DB[module_key][topic_key]
    if challenge_key not in topic_db:
        return False, "Challenge not found in topic catalog."
        
    challenge_info = topic_db[challenge_key]
    
    # Define Target Directory
    topic_dir = os.path.join(module_key, topic_key)
    challenge_dir = os.path.join(topic_dir, challenge_key)
    os.makedirs(challenge_dir, exist_ok=True)
    
    # 1. Create __init__.py markers to declare packages (resolving pytest import mismatches)
    with open(os.path.join(module_key, "__init__.py"), "w") as f:
        f.write("# Package marker\n")
    with open(os.path.join(topic_dir, "__init__.py"), "w") as f:
        f.write("# Package marker\n")
    with open(os.path.join(challenge_dir, "__init__.py"), "w") as f:
        f.write("# Package marker\n")
        
    # 2. Topic Concept README
    readme_path = os.path.join(topic_dir, "README.md")
    if not os.path.exists(readme_path):
        readme_title = topic_key.replace("_", " ").title()
        default_readme = f"# {readme_title}\n\nConcept card for {readme_title}.\n\n### 🏢 Real-World Application\nHigh scalability configurations."
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(default_readme)
            
    # 3. Challenge-specific README
    challenge_readme_path = os.path.join(challenge_dir, "README.md")
    if not os.path.exists(challenge_readme_path):
        challenge_readme = challenge_info.get("readme_content")
        if not challenge_readme:
            title = challenge_key.split("_", 1)[1].replace("_", " ").title() if "_" in challenge_key else challenge_key.title()
            challenge_readme = f"# {title}\n\n{challenge_info.get('description', '')}"
        with open(challenge_readme_path, "w", encoding="utf-8") as f:
            f.write(challenge_readme)
            
    # File Paths
    file_type = challenge_info.get("type", "code") if "type" in challenge_info else ("design" if challenge_key.endswith(".md") else "code")
    
    if file_type == "code":
        # Code challenge creation (.py)
        code_filename = f"{challenge_key}.py"
        test_filename = f"{challenge_key}_test.py"
        
        code_path = os.path.join(challenge_dir, code_filename)
        test_path = os.path.join(challenge_dir, test_filename)
        
        # Parse names
        func_name = extract_function_name(challenge_info.get("starter_code"))
        
        # Write template python script
        if not os.path.exists(code_path):
            starter = challenge_info.get("starter_code") or f"def {func_name}():\n    # Write your solution here\n    pass"
            desc = challenge_info.get("description", "Solve the challenge.")
            link = challenge_info.get("link", "")
            solutions = challenge_info.get("solutions") or f"# --- APPROACH 1: Optimal ---\ndef {func_name}_optimal():\n    pass"
            
            code_content = f'"""\nChallenge: {challenge_key}\nDifficulty: {challenge_info.get("difficulty", "Medium")}\nLink: {link}\n\nProblem:\n{desc}\n"""\n\n# --- STARTER TEMPLATE FOR USER ---\n{starter}\n\n# =====================================================================\n# PLURAL SOLUTIONS & COMPLEXITY ANALYSIS\n# =====================================================================\n\n{solutions}\n'
            
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code_content)
                
        # Write test script
        if not os.path.exists(test_path):
            test_cases = challenge_info.get("test_code") or f"def test_basic():\n    # Add assertions here\n    pass"
            
            test_content = f"""import os
import sys
import inspect

# Ensure local directory is in path for resolving local imports temporarily
dir_path = os.path.dirname(os.path.abspath(__file__))
if dir_path not in sys.path:
    sys.path.insert(0, dir_path)

try:
    # Try importing from the sandbox file first
    from {challenge_key}_sandbox import {func_name}
except ImportError:
    # Fallback to standard solution
    from {challenge_key} import {func_name}
    try:
        source = inspect.getsource({func_name})
        if "pass" in source:
            # Load optimal version for verification out of the box
            from {challenge_key} import {func_name}_optimal as {func_name}
    except Exception:
        pass

# Clean up path immediately to prevent polluting other test namespaces
if sys.path[0] == dir_path:
    sys.path.pop(0)

{test_cases}
"""
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(test_content)
    else:
        # Design challenge creation (.md)
        design_filename = f"{challenge_key}.md"
        sol_filename = f"{challenge_key}_solution.md"
        
        design_path = os.path.join(challenge_dir, design_filename)
        sol_path = os.path.join(challenge_dir, sol_filename)
        
        if not os.path.exists(design_path):
            desc = challenge_info.get("description", "Design this system.")
            design_content = f"# System Design Challenge: {challenge_key.replace('_', ' ').title()}\n\n{desc}\n"
            with open(design_path, "w", encoding="utf-8") as f:
                f.write(design_content)
                
        if not os.path.exists(sol_path):
            sol_content = challenge_info.get("solutions") or f"# System Design Solution: {challenge_key.replace('_', ' ').title()}\n\nDetailed system components."
            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(sol_content)
                
    return True, f"Challenge {challenge_key} successfully initialized."
