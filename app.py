import streamlit as st
import os
import sys
import subprocess
import ast
import re
import google.generativeai as genai
import importlib
import questions_db
importlib.reload(questions_db)
from questions_db import CHALLENGES_DB
from generator import initialize_challenge

# Page Configuration
st.set_page_config(
    page_title="Interview Prep Vault",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Apply Fonts */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Global Dark Theme Overrides */
.stApp {
    background-color: #0A0D14;
    color: #E2E8F0;
}

/* Sidebar Custom Styling */
[data-testid="stSidebar"] {
    background-color: #0F131E;
    border-right: 1px solid #1E293B;
}

/* Tab Bar Custom Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 2px solid #1E293B;
}

.stTabs [data-baseweb="tab"] {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    color: #94A3B8;
    font-weight: 500;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #F8FAFC;
    background-color: #1F2937;
}

.stTabs [aria-selected="true"] {
    color: #818CF8 !important;
    background-color: #1E1B4B !important;
    border-color: #4F46E5 !important;
    font-weight: 600;
}

/* Custom Concept Cards */
.concept-card {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.concept-title {
    color: #818CF8;
    font-size: 1.15rem;
    font-weight: 600;
    margin-bottom: 10px;
    border-bottom: 1px solid #1E293B;
    padding-bottom: 6px;
}

/* Code sandbox background adjustment */
textarea {
    background-color: #090D16 !important;
    color: #F8FAFC !important;
    font-family: 'JetBrains Mono', monospace !important;
    border: 1px solid #334155 !important;
    border-radius: 6px !important;
}

/* Custom terminal console for tests */
.terminal-window {
    background-color: #05070C;
    border: 1px solid #1E293B;
    border-radius: 8px;
    margin-top: 15px;
    overflow: hidden;
}

.terminal-header {
    background-color: #0F131E;
    border-bottom: 1px solid #1E293B;
    padding: 8px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.terminal-dots {
    display: flex;
    gap: 6px;
}

.dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
}
.dot-red { background-color: #EF4444; }
.dot-yellow { background-color: #F59E0B; }
.dot-green { background-color: #10B981; }

.terminal-title {
    color: #64748B;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
}

.terminal-console {
    color: #F8FAFC;
    font-family: 'JetBrains Mono', monospace;
    border-left: 4px solid #EF4444;
    padding: 14px;
    max-height: 250px;
    overflow-y: auto;
    font-size: 0.85rem;
    white-space: pre-wrap;
    background-color: #05070C;
    margin: 0;
}

.terminal-success {
    color: #34D399;
    font-family: 'JetBrains Mono', monospace;
    border-left: 4px solid #10B981;
    padding: 14px;
    font-size: 0.85rem;
    background-color: #05070C;
    margin: 0;
}

/* Difficulty Badges */
.badge-easy {
    background-color: #064E3B;
    color: #6EE7B7;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-medium {
    background-color: #78350F;
    color: #FDE68A;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}
.badge-hard {
    background-color: #7F1D1D;
    color: #FCA5A5;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* Group Cards */
.group-card {
    background: linear-gradient(135deg, #111827 0%, #0F172A 100%);
    border: 1px solid #1E293B;
    border-radius: 10px;
    padding: 16px 18px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
    min-height: 100px;
}

.group-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    border-radius: 10px 10px 0 0;
}

.group-card:hover {
    transform: translateY(-3px);
    border-color: #4F46E5;
    box-shadow: 0 8px 25px -5px rgba(79, 70, 229, 0.25);
}

.group-card-active {
    border-color: #818CF8 !important;
    box-shadow: 0 0 0 1px #818CF8, 0 8px 25px -5px rgba(79, 70, 229, 0.3) !important;
}

.group-card-name {
    color: #F8FAFC;
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 6px;
}

.group-card-count {
    color: #64748B;
    font-size: 0.8rem;
    margin-top: 4px;
}

.group-card-emoji {
    font-size: 1.5rem;
}

/* Module Section Headers */
.module-section-header {
    color: #F8FAFC;
    font-size: 1.1rem;
    font-weight: 600;
    margin: 20px 0 12px 0;
    padding: 10px 14px;
    border-radius: 8px;
    border-left: 4px solid;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* Progress Bar Animation */
@keyframes progressFill {
    from { width: 0%; }
}

.animated-progress {
    animation: progressFill 1.2s ease-out;
}

/* Search Results Table Header */
.table-header {
    display: grid;
    grid-template-columns: 0.8fr 2.5fr 2fr 2fr 2fr 1.2fr 1.8fr;
    gap: 10px;
    padding: 12px 0;
    border-bottom: 2px solid #1E293B;
    margin-bottom: 8px;
    font-weight: 600;
    color: #94A3B8;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Hero Section */
.hero-section {
    background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #0F172A 100%);
    border: 1px solid #1E293B;
    border-radius: 12px;
    padding: 30px;
    margin-bottom: 24px;
    text-align: center;
}

.hero-title {
    background: linear-gradient(135deg, #818CF8, #C084FC, #F472B6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.hero-subtitle {
    color: #94A3B8;
    font-size: 1rem;
    max-width: 600px;
    margin: 0 auto;
}

/* Stats Cards */
.stat-card {
    background-color: #111827;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #818CF8, #C084FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    color: #64748B;
    font-size: 0.8rem;
    font-weight: 500;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)

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

def get_group_meta(group_name):
    """Get metadata for a group, with fallback defaults."""
    return GROUP_META.get(group_name, {"emoji": "📌", "color": "#94A3B8", "module": ""})

# ─────────────────────────────────────────────────
# SCANNING & INDEXING
# ─────────────────────────────────────────────────
def scan_initialized_challenges():
    initialized = {}
    for module in CHALLENGES_DB:
        initialized[module] = {}
        for topic in CHALLENGES_DB[module]:
            initialized[module][topic] = {}
            topic_dir = os.path.join(module, topic)
            if os.path.exists(topic_dir) and os.path.isdir(topic_dir):
                for filename in os.listdir(topic_dir):
                    if filename.startswith("q") and (filename.endswith(".py") or filename.endswith(".md")) and "test" not in filename and "solution" not in filename:
                        challenge_key = filename[:-3]
                        initialized[module][topic][challenge_key] = True
    return initialized

def collect_all_groups():
    """Collect all unique groups across the entire DB with counts."""
    group_counts = {}
    for m in CHALLENGES_DB:
        for t in CHALLENGES_DB[m]:
            for c in CHALLENGES_DB[m][t]:
                info = CHALLENGES_DB[m][t][c]
                for g in info.get("groups", []):
                    if g not in group_counts:
                        group_counts[g] = {"total": 0, "modules": set()}
                    group_counts[g]["total"] += 1
                    group_counts[g]["modules"].add(m)
    return group_counts

def collect_module_groups(module_key):
    """Collect groups for a specific module."""
    group_counts = {}
    for t in CHALLENGES_DB.get(module_key, {}):
        for c in CHALLENGES_DB[module_key][t]:
            info = CHALLENGES_DB[module_key][t][c]
            for g in info.get("groups", []):
                if g not in group_counts:
                    group_counts[g] = 0
                group_counts[g] += 1
    return group_counts

# ─────────────────────────────────────────────────
# APP STATE INITIALIZATION
# ─────────────────────────────────────────────────
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "Explore Dashboard"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_challenge" not in st.session_state:
    st.session_state.last_challenge = None
if "test_output" not in st.session_state:
    st.session_state.test_output = ""
if "test_success" not in st.session_state:
    st.session_state.test_success = None
if "sandbox_code" not in st.session_state:
    st.session_state.sandbox_code = ""
if "selected_module" not in st.session_state:
    st.session_state.selected_module = "01_DSA"
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = "arrays_and_hashing"
if "selected_challenge" not in st.session_state:
    st.session_state.selected_challenge = "q01_two_sum"
if "selected_group" not in st.session_state:
    st.session_state.selected_group = "All"

# ─────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────
st.sidebar.markdown("<h2 style='color:#818CF8; margin-bottom:5px;'>🧠 PREP VAULT</h2>", unsafe_allow_html=True)
st.sidebar.caption("Monolithic Learning Vault & AI Coach")

initialized_map = scan_initialized_challenges()
all_group_data = collect_all_groups()

total_challenges = sum(len(CHALLENGES_DB[m][t]) for m in CHALLENGES_DB for t in CHALLENGES_DB[m])
initialized_challenges = sum(len(initialized_map.get(m, {}).get(t, {})) for m in CHALLENGES_DB for t in CHALLENGES_DB[m])

st.sidebar.markdown("---")
view_mode = st.sidebar.radio(
    "App View", 
    options=["Explore Dashboard", "Practice Sandbox"],
    index=0 if st.session_state.view_mode == "Explore Dashboard" else 1
)
st.session_state.view_mode = view_mode

# Progress Widget
pct = int(initialized_challenges / total_challenges * 100) if total_challenges > 0 else 0
st.sidebar.markdown(f"""
<div style='background: linear-gradient(135deg, #111827, #0F172A); border: 1px solid #1E293B; padding: 14px; border-radius: 8px; margin: 15px 0;'>
    <div style='font-size: 0.8rem; color: #94A3B8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em;'>WORKSPACE PROGRESS</div>
    <div style='font-size: 1.5rem; color: #818CF8; font-weight: 700; margin: 6px 0;'>{initialized_challenges} / {total_challenges} <span style='font-size: 0.8rem; color:#64748B;'>challenges</span></div>
    <div style='background-color: #1E293B; border-radius: 4px; height: 6px; overflow: hidden;'>
        <div class='animated-progress' style='background: linear-gradient(90deg, #4F46E5, #818CF8); width: {pct}%; height: 100%; border-radius: 4px;'></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Module Selector
module_display_names = {
    "01_DSA": "01. DSA (Algorithms)",
    "02_Data_Science_ML": "02. Data Science & ML",
    "03_LLD": "03. Low-Level Design",
    "04_HLD": "04. High-Level Design"
}

module_options = list(CHALLENGES_DB.keys())
try:
    mod_idx = module_options.index(st.session_state.selected_module)
except ValueError:
    mod_idx = 0

selected_module_key = st.sidebar.selectbox(
    "Select Module",
    options=module_options,
    index=mod_idx,
    format_func=lambda x: module_display_names.get(x, x),
    key="module_selector"
)
st.session_state.selected_module = selected_module_key

# Group Filter Selector (Sidebar)
module_groups = collect_module_groups(selected_module_key)
group_options_sidebar = ["All"] + sorted(module_groups.keys())

try:
    grp_idx = group_options_sidebar.index(st.session_state.selected_group)
except ValueError:
    grp_idx = 0
    st.session_state.selected_group = "All"

selected_group_sidebar = st.sidebar.selectbox(
    "Filter by Group",
    options=group_options_sidebar,
    index=grp_idx,
    format_func=lambda x: f"{get_group_meta(x)['emoji']} {x}" if x != "All" else "🔎 All Groups",
    key="group_selector"
)
st.session_state.selected_group = selected_group_sidebar

# Topic Selector (filtered by group)
topics = CHALLENGES_DB[selected_module_key]
if st.session_state.selected_group != "All":
    filtered_topics = {}
    for t_key in topics:
        for c_key in topics[t_key]:
            if st.session_state.selected_group in topics[t_key][c_key].get("groups", []):
                filtered_topics[t_key] = topics[t_key]
                break
    topic_options = list(filtered_topics.keys()) if filtered_topics else list(topics.keys())
else:
    topic_options = list(topics.keys())

try:
    top_idx = topic_options.index(st.session_state.selected_topic)
except ValueError:
    top_idx = 0
    if topic_options:
        st.session_state.selected_topic = topic_options[0]

selected_topic_key = st.sidebar.selectbox(
    "Select Topic",
    options=topic_options,
    index=top_idx,
    format_func=clean_name,
    key="topic_selector"
)
st.session_state.selected_topic = selected_topic_key

# Challenge Selector
challenges = topics.get(selected_topic_key, {})
if st.session_state.selected_group != "All":
    filtered_challenges = {k: v for k, v in challenges.items() if st.session_state.selected_group in v.get("groups", [])}
    challenge_options = list(filtered_challenges.keys()) if filtered_challenges else list(challenges.keys())
else:
    challenge_options = list(challenges.keys())

try:
    chal_idx = challenge_options.index(st.session_state.selected_challenge)
except ValueError:
    chal_idx = 0
    if challenge_options:
        st.session_state.selected_challenge = challenge_options[0]

def format_challenge_name(challenge_key):
    is_active = initialized_map.get(selected_module_key, {}).get(selected_topic_key, {}).get(challenge_key, False)
    dot = "🟢" if is_active else "⚪"
    return f"{dot} {clean_name(challenge_key)}"

selected_challenge_key = st.sidebar.selectbox(
    "Select Challenge",
    options=challenge_options,
    index=chal_idx,
    format_func=format_challenge_name,
    key="challenge_selector"
)
st.session_state.selected_challenge = selected_challenge_key
challenge_info = challenges.get(selected_challenge_key, {})

# Sidebar AI Configuration
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#F8FAFC; font-size:1.0rem; margin-bottom:5px;'>⚙️ AI Settings</h3>", unsafe_allow_html=True)
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

model_options = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
selected_model = st.sidebar.selectbox("Gemini Model", options=model_options, index=0)

# Resolve Paths
physical_topic_dir = os.path.join(selected_module_key, selected_topic_key)
physical_challenge_path = os.path.join(physical_topic_dir, f"{selected_challenge_key}.py")
if not os.path.exists(physical_challenge_path):
    physical_challenge_path = os.path.join(physical_topic_dir, f"{selected_challenge_key}.md")

is_challenge_active = initialized_map.get(selected_module_key, {}).get(selected_topic_key, {}).get(selected_challenge_key, False)

# Reset session code on selection change
current_challenge_id = f"{selected_module_key}/{selected_topic_key}/{selected_challenge_key}"
if current_challenge_id != st.session_state.last_challenge:
    st.session_state.last_challenge = current_challenge_id
    st.session_state.chat_history = []
    st.session_state.test_output = ""
    st.session_state.test_success = None
    if is_challenge_active and os.path.exists(physical_challenge_path) and physical_challenge_path.endswith(".py"):
        st.session_state.sandbox_code = extract_starter_code(physical_challenge_path)
    else:
        st.session_state.sandbox_code = ""


# ═══════════════════════════════════════════════════
# VIEW 1: EXPLORE DASHBOARD
# ═══════════════════════════════════════════════════
if st.session_state.view_mode == "Explore Dashboard":
    
    # Hero Section
    st.markdown("""
    <div class='hero-section'>
        <div class='hero-title'>🧠 Interview Prep Vault</div>
        <div class='hero-subtitle'>Browse, filter, and track your progress across DSA, ML, LLD, and HLD. Click any group card to filter challenges instantly.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Row
    easy_count = sum(1 for m in CHALLENGES_DB for t in CHALLENGES_DB[m] for c in CHALLENGES_DB[m][t] if CHALLENGES_DB[m][t][c].get("difficulty") == "Easy")
    medium_count = sum(1 for m in CHALLENGES_DB for t in CHALLENGES_DB[m] for c in CHALLENGES_DB[m][t] if CHALLENGES_DB[m][t][c].get("difficulty") == "Medium")
    hard_count = sum(1 for m in CHALLENGES_DB for t in CHALLENGES_DB[m] for c in CHALLENGES_DB[m][t] if CHALLENGES_DB[m][t][c].get("difficulty") == "Hard")
    total_groups = len(all_group_data)
    
    sc1, sc2, sc3, sc4, sc5 = st.columns(5)
    for col, val, label in [(sc1, total_challenges, "Total Challenges"), (sc2, total_groups, "Groups"), (sc3, easy_count, "Easy"), (sc4, medium_count, "Medium"), (sc5, hard_count, "Hard")]:
        with col:
            st.markdown(f"""
            <div class='stat-card'>
                <div class='stat-value'>{val}</div>
                <div class='stat-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
    
    # ─── GROUP CARDS BY MODULE ─── 
    module_meta = {
        "01_DSA":             {"name": "DSA — Data Structures & Algorithms", "color": "#818CF8", "icon": "💻"},
        "02_Data_Science_ML": {"name": "Data Science & Machine Learning", "color": "#34D399", "icon": "📊"},
        "03_LLD":             {"name": "Low-Level Design", "color": "#FBBF24", "icon": "🏗️"},
        "04_HLD":             {"name": "High-Level Design", "color": "#F87171", "icon": "🌐"},
    }
    
    for m_key, m_meta in module_meta.items():
        m_groups = collect_module_groups(m_key)
        if not m_groups:
            continue
            
        st.markdown(f"""
        <div class='module-section-header' style='background: linear-gradient(90deg, {m_meta['color']}15, transparent); border-color: {m_meta['color']};'>
            <span style='font-size: 1.3rem;'>{m_meta['icon']}</span>
            <span>{m_meta['name']}</span>
            <span style='color: #64748B; font-size: 0.85rem; font-weight: 400; margin-left: auto;'>{sum(m_groups.values())} challenges</span>
        </div>
        """, unsafe_allow_html=True)
        
        sorted_groups = sorted(m_groups.items(), key=lambda x: -x[1])
        cols_per_row = 6
        rows = [sorted_groups[i:i+cols_per_row] for i in range(0, len(sorted_groups), cols_per_row)]
        
        for row in rows:
            cols = st.columns(cols_per_row)
            for idx, (g_name, g_count) in enumerate(row):
                with cols[idx]:
                    meta = get_group_meta(g_name)
                    is_active = (st.session_state.selected_group == g_name)
                    active_class = "group-card-active" if is_active else ""
                    
                    if st.button(
                        f"{meta['emoji']} {g_name}\n({g_count})",
                        key=f"grp_{m_key}_{g_name}",
                        use_container_width=True
                    ):
                        if st.session_state.selected_group == g_name:
                            st.session_state.selected_group = "All"
                        else:
                            st.session_state.selected_group = g_name
                            st.session_state.selected_module = m_key
                        st.rerun()
    
    st.markdown("---")
    
    # ─── FILTER BAR ───
    st.markdown("### 🔍 Search & Filter Challenges")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns([5, 2, 2, 2])
    
    with col_s1:
        search_query = st.text_input("Search challenge name or description...", placeholder="Type e.g. Anagram, Linear, TinyURL...")
    with col_s2:
        diff_filter = st.selectbox("Difficulty", options=["All", "Easy", "Medium", "Hard"])
    with col_s3:
        all_groups_list = sorted(all_group_data.keys())
        group_filter = st.selectbox("Group", options=["All"] + all_groups_list, index=([0] + [i+1 for i, g in enumerate(all_groups_list) if g == st.session_state.selected_group])[(-1 if st.session_state.selected_group != "All" else 0)])
    with col_s4:
        all_topics_list = sorted(list(set(clean_name(t) for m in CHALLENGES_DB for t in CHALLENGES_DB[m])))
        topic_filter = st.selectbox("Topic", options=["All"] + all_topics_list)
    
    # Sync group filter with card clicks
    active_group_filter = group_filter if group_filter != "All" else st.session_state.selected_group
    if active_group_filter == "All":
        active_group_filter = None
    
    # Compile Search results
    search_results = []
    for m in CHALLENGES_DB:
        for t in CHALLENGES_DB[m]:
            for c in CHALLENGES_DB[m][t]:
                info = CHALLENGES_DB[m][t][c]
                is_active = initialized_map.get(m, {}).get(t, {}).get(c, False)
                challenge_groups = info.get("groups", [])
                
                # Apply filters
                if search_query:
                    search_lower = search_query.lower()
                    if search_lower not in clean_name(c).lower() and search_lower not in info.get("description", "").lower():
                        continue
                if diff_filter != "All" and info.get("difficulty") != diff_filter:
                    continue
                if active_group_filter and active_group_filter not in challenge_groups:
                    continue
                if topic_filter != "All" and clean_name(t) != topic_filter:
                    continue
                    
                search_results.append({
                    "id": f"{m}/{t}/{c}",
                    "name": clean_name(c),
                    "module": module_display_names.get(m, m),
                    "groups": challenge_groups,
                    "topic": clean_name(t),
                    "difficulty": info.get("difficulty", "Medium"),
                    "status": "🟢 Active" if is_active else "⚪ Inactive",
                    "m_key": m,
                    "t_key": t,
                    "c_key": c
                })
                
    # Display Search Results
    if not search_results:
        st.info("No matching challenges found. Try adjusting your filters.")
    else:
        # Active group filter indicator
        if active_group_filter:
            gm = get_group_meta(active_group_filter)
            st.markdown(f"""
            <div style='display: inline-flex; align-items: center; gap: 8px; background: {gm['color']}20; border: 1px solid {gm['color']}50; padding: 6px 14px; border-radius: 20px; margin-bottom: 12px;'>
                <span>{gm['emoji']}</span>
                <span style='color: {gm['color']}; font-weight: 600;'>Filtering: {active_group_filter}</span>
                <span style='color: #64748B;'>— {len(search_results)} results</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"**Found {len(search_results)} challenges**")
        
        # Table Header
        st.markdown("""
        <div class='table-header'>
            <div>Status</div>
            <div>Challenge</div>
            <div>Module</div>
            <div>Groups</div>
            <div>Topic</div>
            <div>Difficulty</div>
            <div>Action</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Table Rows
        for item in search_results:
            col_t1, col_t2, col_t3, col_t4, col_t5, col_t6, col_t7 = st.columns([0.8, 2.5, 2, 2, 2, 1.2, 1.8])
            
            with col_t1:
                st.write(item["status"])
            with col_t2:
                st.markdown(f"**{item['name']}**")
            with col_t3:
                st.write(item["module"])
            with col_t4:
                # Show group badges
                group_badges = ""
                for g in item["groups"][:3]:  # Show max 3 groups
                    gm = get_group_meta(g)
                    group_badges += f"<span style='background:{gm['color']}20; color:{gm['color']}; padding:2px 6px; border-radius:3px; font-size:0.7rem; margin-right:3px;'>{g}</span>"
                if len(item["groups"]) > 3:
                    group_badges += f"<span style='color:#64748B; font-size:0.7rem;'>+{len(item['groups'])-3}</span>"
                st.markdown(group_badges, unsafe_allow_html=True)
            with col_t5:
                st.write(item["topic"])
            with col_t6:
                badge = item["difficulty"]
                if badge == "Easy": st.markdown("<span style='color:#6EE7B7;'>Easy</span>", unsafe_allow_html=True)
                elif badge == "Medium": st.markdown("<span style='color:#FDE68A;'>Medium</span>", unsafe_allow_html=True)
                else: st.markdown("<span style='color:#FCA5A5;'>Hard</span>", unsafe_allow_html=True)
            with col_t7:
                if st.button("💻 Solve", key=f"btn_{item['id']}"):
                    st.session_state.selected_module = item["m_key"]
                    st.session_state.selected_topic = item["t_key"]
                    st.session_state.selected_challenge = item["c_key"]
                    st.session_state.view_mode = "Practice Sandbox"
                    st.rerun()
            st.markdown("<hr style='margin:4px 0; border-color:#1E293B;'/>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════
# VIEW 2: PRACTICE SANDBOX
# ═══════════════════════════════════════════════════
else:
    col1, col2 = st.columns([7, 5])
    
    with col1:
        # Header card
        badge_html = get_difficulty_badge(challenge_info.get("difficulty"))
        challenge_groups = challenge_info.get("groups", [])
        group_pills = ""
        for g in challenge_groups:
            gm = get_group_meta(g)
            group_pills += f"<span style='background:{gm['color']}20; color:{gm['color']}; padding:3px 8px; border-radius:4px; font-size:0.75rem; margin-right:4px;'>{gm['emoji']} {g}</span>"
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0F131E, #1E1B4B20); border: 1px solid #1E293B; padding: 18px 22px; border-radius: 10px; margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h3 style='margin: 0; color: #F8FAFC;'>{clean_name(selected_challenge_key)}</h3>
                <div>{badge_html}</div>
            </div>
            <p style='color: #64748B; font-size: 0.9rem; margin: 8px 0 0 0;'>
                Module: <strong>{module_display_names.get(selected_module_key, selected_module_key)}</strong> | Topic: <strong>{clean_name(selected_topic_key)}</strong>
            </p>
            <div style='margin-top: 8px;'>{group_pills}</div>
        </div>
        """, unsafe_allow_html=True)

        if not is_challenge_active:
            st.markdown(f"""
            <div style='background-color: #111827; border: 1px solid #1E293B; padding: 24px; border-radius: 8px; text-align: center; margin-bottom: 20px;'>
                <h4 style='color: #818CF8; margin-top: 0;'>⚪ Challenge not initialized physically</h4>
                <p style='color: #94A3B8; font-size: 0.95rem; max-width: 500px; margin: 8px auto 16px auto;'>
                    Initialize this challenge to create the workspace files on your local drive. This generates the concept guide, the starter code file, and the test suites.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🆕 Initialize Challenge Workspace Files", type="primary", use_container_width=True):
                success, msg = initialize_challenge(selected_module_key, selected_topic_key, selected_challenge_key)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
                    
            st.markdown("### Challenge Description")
            st.markdown(f"```text\n{challenge_info.get('description')}\n```")
            if challenge_info.get("link"):
                st.markdown(f"🔗 **Resource Link**: [Go to original loop]({challenge_info.get('link')})")

        else:
            tabs = st.tabs(["📖 Learn & Concept", "💻 Sandbox", "💡 Solutions"])
            is_code_type = physical_challenge_path.endswith(".py")
            
            # TAB 1: Learn & Concept
            with tabs[0]:
                readme_path = os.path.join(physical_topic_dir, "README.md")
                if os.path.exists(readme_path):
                    with open(readme_path, "r", encoding="utf-8") as f:
                        st.markdown(f.read())
                else:
                    st.info("No concept guide available.")
                    
                st.markdown("---")
                st.markdown("### Challenge Description & Guidelines")
                if is_code_type:
                    st.markdown(f"```text\n{extract_docstring(physical_challenge_path)}\n```")
                    if challenge_info.get("link"):
                        st.markdown(f"🔗 **Resource Link**: [Go to original loop]({challenge_info.get('link')})")
                else:
                    with open(physical_challenge_path, "r", encoding="utf-8") as f:
                        st.markdown(f.read())

            # TAB 2: Sandbox
            with tabs[1]:
                if is_code_type:
                    st.markdown("#### Code Sandbox")
                    st.caption("Write your implementation below. The test cases will execute directly against this structure:")
                    user_code = st.text_area(
                        "Python Editor", 
                        value=st.session_state.sandbox_code, 
                        height=300, 
                        label_visibility="collapsed"
                    )
                    st.session_state.sandbox_code = user_code
                    
                    test_filename = f"{selected_challenge_key}_test.py"
                    test_path = os.path.join(physical_topic_dir, test_filename)
                    
                    c_btn1, c_btn2, c_btn3 = st.columns([1.5, 1.5, 5])
                    
                    with c_btn1:
                        run_tests_btn = st.button("🚀 Run Tests", type="primary", use_container_width=True)
                    with c_btn2:
                        reset_btn = st.button("🔄 Reset Code", use_container_width=True)
                    
                    if reset_btn:
                        st.session_state.sandbox_code = extract_starter_code(physical_challenge_path)
                        st.rerun()

                    if run_tests_btn:
                        sandbox_filename = f"{selected_challenge_key}_sandbox.py"
                        sandbox_path = os.path.join(physical_topic_dir, sandbox_filename)
                        
                        with open(sandbox_path, "w", encoding="utf-8") as f:
                            f.write(user_code)
                        
                        with st.spinner("Executing test suite in Pytest..."):
                            cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            
                        if os.path.exists(sandbox_path):
                            os.remove(sandbox_path)
                        
                        st.session_state.test_output = result.stdout + "\n" + result.stderr
                        st.session_state.test_success = (result.returncode == 0)
                        st.rerun()
                        
                    if st.session_state.test_output:
                        st.markdown("""
                        <div class='terminal-window'>
                            <div class='terminal-header'>
                                <div class='terminal-dots'>
                                    <div class='dot dot-red'></div>
                                    <div class='dot dot-yellow'></div>
                                    <div class='dot dot-green'></div>
                                </div>
                                <div class='terminal-title'>bash - pytest results</div>
                                <div></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.session_state.test_success:
                            st.markdown("<div class='terminal-success'>🎉 ALL TESTS PASSED SUCCESSFULLY!</div>", unsafe_allow_html=True)
                            st.code(st.session_state.test_output, language="text")
                        else:
                            st.markdown("<div class='terminal-console'>❌ TEST RUN FAILED. Failure details below:</div>", unsafe_allow_html=True)
                            st.code(st.session_state.test_output, language="text")
                else:
                    st.markdown("#### Design Architecture Sandbox")
                    st.caption("Outline your high-level system components, DB design, API schemas, and load management:")
                    user_design = st.text_area(
                        "System Design Draft",
                        value=st.session_state.sandbox_code,
                        placeholder="# 1. Requirements & System SLAs\n# 2. System Architecture & Component Mapping\n# 3. Database Schema Layout\n# 4. Asynchronous Queue Scaling & Retries...",
                        height=350,
                        label_visibility="collapsed"
                    )
                    st.session_state.sandbox_code = user_design
                    
                    if st.button("💾 Save Design Draft"):
                        st.success("Draft saved successfully! You can discuss this setup with the AI Coach on the right pane, or click the 'Solutions' tab to view the production architecture blueprint.")

            # TAB 3: Solutions
            with tabs[2]:
                if is_code_type:
                    st.markdown(f"""
                    <div class='concept-card'>
                        <div class='concept-title'>⚡ Solution Approaches</div>
                        <p style="color: #94A3B8; font-size: 0.95rem; margin-top: 5px;">
                            Below you'll find different approaches to solving this challenge. We recommend understanding the brute force approach first before moving to the optimal solution. Try implementing the optimal solution in the Sandbox yourself!
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    solutions_content = extract_solutions(physical_challenge_path)
                    parsed_approaches = parse_solutions(solutions_content)
                    
                    if parsed_approaches:
                        sub_names = [name for name, _ in parsed_approaches]
                        sub_tabs = st.tabs(sub_names)
                        for sub_tab, (title, code) in zip(sub_tabs, parsed_approaches):
                            with sub_tab:
                                if "Overview" in title:
                                    st.markdown(code)
                                elif "java" in title.lower():
                                    st.code(code, language="java")
                                else:
                                    st.code(code, language="python")
                    else:
                        st.code(solutions_content, language="python")
                else:
                    sol_filename = f"{selected_challenge_key}_solution.md"
                    sol_path = os.path.join(physical_topic_dir, sol_filename)
                    if os.path.exists(sol_path):
                        with open(sol_path, "r", encoding="utf-8") as f:
                            st.markdown(f.read())
                    else:
                        st.info("No written solution guide available.")

    # ─── RIGHT PANEL: AI COACH ───
    with col2:
        st.markdown("### 💬 AI Study Coach")
        
        if not api_key:
            st.info("Enter your Gemini API key in the sidebar to activate the AI Coach.")
            st.stop()
            
        current_challenge_desc = challenge_info.get("description", "Study this concept.")
        system_prompt = f"""You are an elite Staff AI Engineer and Technical Interviewer.
You are helping the user study for technical coding/systems engineering loops.
Currently, they are looking at:
- Module: {selected_module_key}
- Topic: {selected_topic_key}
- Challenge: {selected_challenge_key}
- Groups: {', '.join(challenge_info.get('groups', []))}
- Status: {"Active (Files Initialized)" if is_challenge_active else "Uninitialized"}

Challenge Description:
{current_challenge_desc}

User's Sandbox Draft:
{st.session_state.sandbox_code}

Last Test Execution Success: {st.session_state.test_success}
Last Test/Sandbox Output Logs:
{st.session_state.test_output}

Guidelines:
1. Act as a Socratic tutor. Guide the user with hints and explanations rather than giving them the exact code solution.
2. If they hit a pytest compiler error, explain the error clearly and ask them clarifying questions to fix the logic.
3. Encourage them to verify time and space complexity ($O(N)$ etc.).
4. Do not use too many emojis. Keep the tone professional, helpful, and concise.
"""

        chat_container = st.container(height=450)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])
                    
        if user_message := st.chat_input("Ask a hint or clarify concept..."):
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_message)
            
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(
                    model_name=selected_model,
                    system_instruction=system_prompt
                )
                
                prompt_context = "Historical chat conversation:\n"
                for h in st.session_state.chat_history[:-1]:
                    prompt_context += f"{h['role'].capitalize()}: {h['content']}\n"
                prompt_context += f"User Current Message: {user_message}"
                
                with st.spinner("AI thinking..."):
                    response = model.generate_content(prompt_context)
                    ai_response = response.text
                    
                with chat_container:
                    with st.chat_message("assistant"):
                        st.write(ai_response)
                
                st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
                
            except Exception as e:
                st.error(f"Failed to communicate with Gemini API: {str(e)}")
                st.warning("Hint: If you hit a 404 model not found error, try changing the Gemini Model selection in the sidebar.")
