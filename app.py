import streamlit as st
import os
import sys
import importlib
import questions_db
from questions_db import CHALLENGES_DB
from styles import CSS_STYLING
from helpers import (
    clean_name,
    get_group_meta,
    scan_initialized_challenges,
    collect_all_groups,
    collect_module_groups,
    extract_starter_code,
    module_display_names
)
from dashboard_view import render_dashboard
from sandbox_view import render_sandbox
from ai_coach_view import render_ai_coach_button

# ─────────────────────────────────────────────────
# PAGE CONFIG & STYLING
# ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Prep Vault",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown(CSS_STYLING, unsafe_allow_html=True)

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
# CASCADING SELECTBOX STATE SYNCHRONIZATION
# ─────────────────────────────────────────────────
# Sync session state variables from the selector widget inputs if they were changed
if "module_selector" in st.session_state and st.session_state.module_selector != st.session_state.selected_module:
    st.session_state.selected_module = st.session_state.module_selector
    
    # Cascade reset: set topic to the first topic in the new module
    topics_list = list(CHALLENGES_DB[st.session_state.selected_module].keys())
    st.session_state.selected_topic = topics_list[0]
    
    # Cascade reset: set challenge to the first challenge in the new topic
    challenges_list = list(CHALLENGES_DB[st.session_state.selected_module][st.session_state.selected_topic].keys())
    st.session_state.selected_challenge = challenges_list[0]
    
    # Write back to selectbox widgets
    st.session_state.topic_selector = st.session_state.selected_topic
    st.session_state.challenge_selector = st.session_state.selected_challenge

if "topic_selector" in st.session_state and st.session_state.topic_selector != st.session_state.selected_topic:
    st.session_state.selected_topic = st.session_state.topic_selector
    
    # Cascade reset: set challenge to the first challenge in the new topic
    challenges_list = list(CHALLENGES_DB[st.session_state.selected_module][st.session_state.selected_topic].keys())
    st.session_state.selected_challenge = challenges_list[0]
    
    # Write back to selectbox widget
    st.session_state.challenge_selector = st.session_state.selected_challenge

if "challenge_selector" in st.session_state and st.session_state.challenge_selector != st.session_state.selected_challenge:
    st.session_state.selected_challenge = st.session_state.challenge_selector

# ─── Filtering lists according to Selected Group ───
topics = CHALLENGES_DB[st.session_state.selected_module]
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

# Reset topic selection if current topic is not in options
if st.session_state.selected_topic not in topic_options:
    st.session_state.selected_topic = topic_options[0] if topic_options else list(topics.keys())[0]
    st.session_state.topic_selector = st.session_state.selected_topic

challenges = topics.get(st.session_state.selected_topic, {})
if st.session_state.selected_group != "All":
    filtered_challenges = {k: v for k, v in challenges.items() if st.session_state.selected_group in v.get("groups", [])}
    challenge_options = list(filtered_challenges.keys()) if filtered_challenges else list(challenges.keys())
else:
    challenge_options = list(challenges.keys())

# Reset challenge selection if current challenge is not in options
if st.session_state.selected_challenge not in challenge_options:
    st.session_state.selected_challenge = challenge_options[0] if challenge_options else list(challenges.keys())[0]
    st.session_state.challenge_selector = st.session_state.selected_challenge

# ─── Load dynamic question state for sandbox ───
initialized_map = scan_initialized_challenges(CHALLENGES_DB)
physical_challenge_dir = os.path.join(st.session_state.selected_module, st.session_state.selected_topic, st.session_state.selected_challenge)
physical_challenge_path = os.path.join(physical_challenge_dir, f"{st.session_state.selected_challenge}.py")
if not os.path.exists(physical_challenge_path):
    physical_challenge_path = os.path.join(physical_challenge_dir, f"{st.session_state.selected_challenge}.md")

is_challenge_active = initialized_map.get(st.session_state.selected_module, {}).get(st.session_state.selected_topic, {}).get(st.session_state.selected_challenge, False)

# Clean/Initialize editor state on challenge change
current_challenge_id = f"{st.session_state.selected_module}/{st.session_state.selected_topic}/{st.session_state.selected_challenge}"
if current_challenge_id != st.session_state.last_challenge:
    st.session_state.last_challenge = current_challenge_id
    st.session_state.chat_history = []
    st.session_state.test_output = ""
    st.session_state.test_success = None
    if is_challenge_active and os.path.exists(physical_challenge_path) and physical_challenge_path.endswith(".py"):
        st.session_state.sandbox_code = extract_starter_code(physical_challenge_path)
    else:
        st.session_state.sandbox_code = ""

# ─────────────────────────────────────────────────
# SIDEBAR NAVIGATION & SELECTBOXES
# ─────────────────────────────────────────────────
st.sidebar.markdown("<h2 style='color:#818CF8; margin-bottom:5px;'>🧠 PREP VAULT</h2>", unsafe_allow_html=True)
st.sidebar.caption("Monolithic Learning Vault & AI Coach")

all_group_data = collect_all_groups(CHALLENGES_DB)
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

# Render Dropdowns in Sidebar
module_options = list(CHALLENGES_DB.keys())
mod_idx = module_options.index(st.session_state.selected_module)
selected_module_key = st.sidebar.selectbox(
    "Select Module",
    options=module_options,
    index=mod_idx,
    format_func=lambda x: module_display_names.get(x, x),
    key="module_selector"
)

module_groups = collect_module_groups(CHALLENGES_DB, st.session_state.selected_module)
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

top_idx = topic_options.index(st.session_state.selected_topic)
selected_topic_key = st.sidebar.selectbox(
    "Select Topic",
    options=topic_options,
    index=top_idx,
    format_func=clean_name,
    key="topic_selector"
)

chal_idx = challenge_options.index(st.session_state.selected_challenge)
selected_challenge_key = st.sidebar.selectbox(
    "Select Challenge",
    options=challenge_options,
    index=chal_idx,
    format_func=lambda x: f"{'🟢' if initialized_map.get(st.session_state.selected_module, {}).get(st.session_state.selected_topic, {}).get(x, False) else '⚪'} {clean_name(x)}",
    key="challenge_selector"
)

# AI Configurations
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color:#F8FAFC; font-size:1.0rem; margin-bottom:5px;'>⚙️ AI Settings</h3>", unsafe_allow_html=True)
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=os.environ.get("GEMINI_API_KEY", ""))
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

model_options = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
selected_model = st.sidebar.selectbox("Gemini Model", options=model_options, index=0)

# ─────────────────────────────────────────────────
# VIEW RENDERING
# ─────────────────────────────────────────────────
if st.session_state.view_mode == "Explore Dashboard":
    render_dashboard(initialized_map, all_group_data, total_challenges)
else:
    challenge_info = CHALLENGES_DB[st.session_state.selected_module][st.session_state.selected_topic][st.session_state.selected_challenge]
    render_sandbox(
        st.session_state.selected_module,
        st.session_state.selected_topic,
        st.session_state.selected_challenge,
        challenge_info,
        is_challenge_active
    )

# ─────────────────────────────────────────────────
# AI COACH OVERLAY POPUP
# ─────────────────────────────────────────────────
if st.session_state.view_mode == "Practice Sandbox":
    challenge_info = CHALLENGES_DB[st.session_state.selected_module][st.session_state.selected_topic][st.session_state.selected_challenge]
    render_ai_coach_button(
        st.session_state.selected_module,
        st.session_state.selected_topic,
        st.session_state.selected_challenge,
        challenge_info,
        is_challenge_active,
        api_key,
        selected_model
    )
