import os
import ast
import re

# ─────────────────────────────────────────────────
# GROUP METADATA — colors, emojis, module assignments
# ─────────────────────────────────────────────────
GROUP_META = {
    # DSA Groups
    "Array":                {"emoji": "📊", "color": "#818CF8", "module": "01_DSA"},
    "String":               {"emoji": "🔤", "color": "#A78BFA", "module": "01_DSA"},
    "Hashing":              {"emoji": "#️⃣",  "color": "#6EE7B7", "module": "01_DSA"},
    "Two Pointers":         {"emoji": "👉", "color": "#38BDF8", "module": "01_DSA"},
    "Sliding Window":       {"emoji": "🪟", "color": "#22D3EE", "module": "01_DSA"},
    "Stack & Queue":        {"emoji": "📚", "color": "#FB923C", "module": "01_DSA"},
    "Binary Search":        {"emoji": "🔍", "color": "#F472B6", "module": "01_DSA"},
    "Linked List":          {"emoji": "🔗", "color": "#C084FC", "module": "01_DSA"},
    "Tree":                 {"emoji": "🌳", "color": "#34D399", "module": "01_DSA"},
    "Heap / Priority Queue":{"emoji": "⛰️", "color": "#FBBF24", "module": "01_DSA"},
    "Graph":                {"emoji": "🕸️", "color": "#F87171", "module": "01_DSA"},
    "Dynamic Programming":  {"emoji": "🧩", "color": "#E879F9", "module": "01_DSA"},
    "Backtracking":         {"emoji": "↩️", "color": "#FDA4AF", "module": "01_DSA"},
    "Matrix":               {"emoji": "🔢", "color": "#67E8F9", "module": "01_DSA"},
    "Math":                 {"emoji": "➗", "color": "#D9F99D", "module": "01_DSA"},
    # ML Groups
    "Classical ML":         {"emoji": "📈", "color": "#34D399", "module": "02_Data_Science_ML"},
    "Deep Learning":        {"emoji": "🧠", "color": "#818CF8", "module": "02_Data_Science_ML"},
    "Evaluation & Metrics": {"emoji": "📏", "color": "#FBBF24", "module": "02_Data_Science_ML"},
    "Optimization":         {"emoji": "⚡", "color": "#FB923C", "module": "02_Data_Science_ML"},
    "Transformers":         {"emoji": "🤖", "color": "#A78BFA", "module": "02_Data_Science_ML"},
    "Computer Vision":      {"emoji": "👁️", "color": "#22D3EE", "module": "02_Data_Science_ML"},
    "Sequence Models":      {"emoji": "📜", "color": "#F472B6", "module": "02_Data_Science_ML"},
    "Graph Neural Networks":{"emoji": "🕸️", "color": "#F87171", "module": "02_Data_Science_ML"},
    "Unsupervised Learning":{"emoji": "🔮", "color": "#C084FC", "module": "02_Data_Science_ML"},
    "Ensemble Methods":     {"emoji": "🌲", "color": "#6EE7B7", "module": "02_Data_Science_ML"},
    "Probabilistic Models": {"emoji": "🎲", "color": "#FDA4AF", "module": "02_Data_Science_ML"},
    "Dimensionality Reduction": {"emoji": "📐", "color": "#67E8F9", "module": "02_Data_Science_ML"},
    # LLD Groups
    "Creational Patterns":  {"emoji": "🏗️", "color": "#FBBF24", "module": "03_LLD"},
    "Structural Patterns":  {"emoji": "🧱", "color": "#FB923C", "module": "03_LLD"},
    "Behavioral Patterns":  {"emoji": "🎭", "color": "#F472B6", "module": "03_LLD"},
    "OOP Case Studies":     {"emoji": "🏛️", "color": "#818CF8", "module": "03_LLD"},
    "Concurrency":          {"emoji": "🔄", "color": "#22D3EE", "module": "03_LLD"},
    "Caching & Storage":    {"emoji": "💾", "color": "#34D399", "module": "03_LLD"},
    "Messaging":            {"emoji": "📨", "color": "#A78BFA", "module": "03_LLD"},
    "Game Design":          {"emoji": "🎮", "color": "#F87171", "module": "03_LLD"},
    # HLD Groups
    "Distributed Systems":  {"emoji": "🌐", "color": "#818CF8", "module": "04_HLD"},
    "Networking":           {"emoji": "📡", "color": "#22D3EE", "module": "04_HLD"},
    "Databases":            {"emoji": "🗄️", "color": "#34D399", "module": "04_HLD"},
    "Real-World Systems":   {"emoji": "🏢", "color": "#F87171", "module": "04_HLD"},
    "Data Pipelines":       {"emoji": "🔁", "color": "#FBBF24", "module": "04_HLD"},
}

module_display_names = {
    "01_DSA": "01. DSA (Algorithms)",
    "02_Data_Science_ML": "02. Data Science & ML",
    "03_LLD": "03. Low-Level Design",
    "04_HLD": "04. High-Level Design"
}

def get_group_meta(group_name):
    """Get metadata for a group, with fallback defaults."""
    return GROUP_META.get(group_name, {"emoji": "📌", "color": "#94A3B8", "module": ""})

# ─────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────
def extract_docstring(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        docstring = ast.get_docstring(tree)
        if docstring:
            return docstring
    except Exception:
        pass
    return "No challenge description available."

def extract_starter_code(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        start_marker = "# --- STARTER TEMPLATE FOR USER ---"
        end_marker = "# ====================================================================="
        
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return content
        start_idx += len(start_marker)
        end_idx = content.find(end_marker, start_idx)
        if end_idx == -1:
            return content[start_idx:].strip()
        return content[start_idx:end_idx].strip()
    except Exception as e:
        return f"# Error loading starter template: {str(e)}"

def extract_solutions(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        end_marker = "# ====================================================================="
        idx = content.find(end_marker)
        if idx == -1:
            return content
        return content[idx + len(end_marker):].strip()
    except Exception as e:
        return f"Error loading solutions: {str(e)}"

def clean_name(name):
    cleaned = name
    if "_" in cleaned and (cleaned[:2].isdigit() or (cleaned.startswith("q") and cleaned[1:3].isdigit())):
        parts = cleaned.split("_", 1)
        cleaned = parts[1]
    if cleaned.endswith(".py"):
        cleaned = cleaned[:-3]
    elif cleaned.endswith(".md"):
        cleaned = cleaned[:-3]
    return cleaned.replace("_", " ").title()

def get_difficulty_badge(difficulty):
    if difficulty == "Easy":
        return "<span class='badge-easy'>Easy</span>"
    elif difficulty == "Medium":
        return "<span class='badge-medium'>Medium</span>"
    elif difficulty == "Hard":
        return "<span class='badge-hard'>Hard</span>"
    return ""

def parse_solutions(solutions_content):
    """
    Parses solutions_content into separate syntax-highlighted tabs
    by splitting on '# --- APPROACH' or '# Approach' indicators.
    """
    pattern = r"(#\s*(?:---\s*)?APPROACH\s*\d+:.*?(?:\s*---)?|#\s*---\s*.*?\s*---)\n"
    parts = re.split(pattern, solutions_content, flags=re.IGNORECASE)
    
    if len(parts) <= 1:
        return [("Full Solution", solutions_content)]
        
    approaches = []
    
    overview = parts[0].strip()
    if overview:
        cleaned_lines = [l for l in overview.split("\n") if not l.strip().startswith("# ==")]
        cleaned_overview = "\n".join(cleaned_lines).strip()
        if cleaned_overview:
            approaches.append(("Overview", cleaned_overview))
            
    for i in range(1, len(parts), 2):
        header = parts[i].replace("#", "").replace("-", "").strip()
        content = parts[i+1].strip()
        
        if "java" in header.lower() or "java" in content.lower():
            if content.startswith("'''") or content.startswith('"""'):
                content = content[3:]
            if content.endswith("'''") or content.endswith('"""'):
                content = content[:-3]
            content = content.strip()
            
        if content:
            approaches.append((header, content))
            
    return approaches

# ─────────────────────────────────────────────────
# SCANNING & INDEXING
# ─────────────────────────────────────────────────
def scan_initialized_challenges(challenges_db):
    initialized = {}
    for module in challenges_db:
        initialized[module] = {}
        for topic in challenges_db[module]:
            initialized[module][topic] = {}
            for challenge_key in challenges_db[module][topic]:
                # In the new structure, user files are inside module/topic/challenge_key/
                challenge_dir = os.path.join(module, topic, challenge_key)
                if os.path.exists(challenge_dir) and os.path.isdir(challenge_dir):
                    py_path = os.path.join(challenge_dir, f"{challenge_key}.py")
                    md_path = os.path.join(challenge_dir, f"{challenge_key}.md")
                    if os.path.exists(py_path) or os.path.exists(md_path):
                        initialized[module][topic][challenge_key] = True
    return initialized

def collect_all_groups(challenges_db):
    """Collect all unique groups across the entire DB with counts."""
    group_counts = {}
    for m in challenges_db:
        for t in challenges_db[m]:
            for c in challenges_db[m][t]:
                info = challenges_db[m][t][c]
                for g in info.get("groups", []):
                    if g not in group_counts:
                        group_counts[g] = {"total": 0, "modules": set()}
                    group_counts[g]["total"] += 1
                    group_counts[g]["modules"].add(m)
    return group_counts

def collect_module_groups(challenges_db, module_key):
    """Collect groups for a specific module."""
    group_counts = {}
    for t in challenges_db.get(module_key, {}):
        for c in challenges_db[module_key][t]:
            info = challenges_db[module_key][t][c]
            for g in info.get("groups", []):
                if g not in group_counts:
                    group_counts[g] = 0
                group_counts[g] += 1
    return group_counts
