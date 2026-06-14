import streamlit as st
from streamlit_ace import st_ace
import os
import sys
import subprocess
from generator import initialize_challenge
from helpers import (
    clean_name,
    get_difficulty_badge,
    get_group_meta,
    extract_docstring,
    extract_starter_code,
    extract_solutions,
    parse_solutions,
    module_display_names
)

def render_sandbox(
    selected_module_key,
    selected_topic_key,
    selected_challenge_key,
    challenge_info,
    is_challenge_active
):
    # Resolve Paths using the new question folder structure
    physical_challenge_dir = os.path.join(selected_module_key, selected_topic_key, selected_challenge_key)
    physical_challenge_path = os.path.join(physical_challenge_dir, f"{selected_challenge_key}.py")
    if not os.path.exists(physical_challenge_path):
        physical_challenge_path = os.path.join(physical_challenge_dir, f"{selected_challenge_key}.md")
        
    badge_html = get_difficulty_badge(challenge_info.get("difficulty"))
    challenge_groups = challenge_info.get("groups", [])
    group_pills = ""
    for g in challenge_groups:
        gm = get_group_meta(g)
        group_pills += f"<span style='background:{gm['color']}20; color:{gm['color']}; padding:3px 8px; border-radius:4px; font-size:0.75rem; margin-right:4px;'>{gm['emoji']} {g}</span>"
    
    # Header card with columns to support Ask Coach button on top
    col_sh1, col_sh2 = st.columns([7.8, 2.2])
    with col_sh1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0F131E, #1E1B4B20); border: 1px solid #1E293B; padding: 18px 22px; border-radius: 10px; margin-bottom: 20px;'>
            <h3 style='margin: 0; color: #F8FAFC;'>{clean_name(selected_challenge_key)}</h3>
            <p style='color: #64748B; font-size: 0.9rem; margin: 8px 0 0 0;'>
                Module: <strong>{module_display_names.get(selected_module_key, selected_module_key)}</strong> | Topic: <strong>{clean_name(selected_topic_key)}</strong>
            </p>
            <div style='margin-top: 8px;'>{group_pills}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_sh2:
        st.markdown(f"<div style='text-align: right; margin-bottom: 12px;'>{badge_html}</div>", unsafe_allow_html=True)
        if st.button("💬 Ask AI Study Coach", key="ask_coach_sandbox_header", use_container_width=True, type="primary"):
            st.session_state.show_ai_coach = not st.session_state.get("show_ai_coach", False)
            st.rerun()

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
            # Try loading challenge-level README first
            challenge_readme_path = os.path.join(physical_challenge_dir, "README.md")
            if os.path.exists(challenge_readme_path):
                with open(challenge_readme_path, "r", encoding="utf-8") as f:
                    st.markdown(f.read())
            else:
                # Fallback to topic-level README
                topic_readme_path = os.path.join(selected_module_key, selected_topic_key, "README.md")
                if os.path.exists(topic_readme_path):
                    with open(topic_readme_path, "r", encoding="utf-8") as f:
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
                
                # Use a challenge-specific key to force Streamlit to recreate/reset the text area when the challenge changes
                user_code = st_ace(
                    value=st.session_state.sandbox_code,
                    language="python",
                    theme="tomorrow_night",
                    keybinding="vscode",
                    tab_size=4,
                    font_size=14,
                    show_gutter=True,
                    show_print_margin=False,
                    wrap=True,
                    auto_update=False,
                    height=350,
                    key=f"code_editor_{selected_challenge_key}"
                )
                st.session_state.sandbox_code = user_code
                
                test_filename = f"{selected_challenge_key}_test.py"
                test_path = os.path.join(physical_challenge_dir, test_filename)
                
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
                    sandbox_path = os.path.join(physical_challenge_dir, sandbox_filename)
                    
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
                
                user_design = st_ace(
                    value=st.session_state.sandbox_code if st.session_state.sandbox_code else "# 1. Requirements & System SLAs\n# 2. System Architecture & Component Mapping\n# 3. Database Schema Layout\n# 4. Asynchronous Queue Scaling & Retries...",
                    language="markdown",
                    theme="tomorrow_night",
                    keybinding="vscode",
                    tab_size=4,
                    font_size=14,
                    show_gutter=True,
                    show_print_margin=False,
                    wrap=True,
                    auto_update=False,
                    height=400,
                    key=f"design_editor_{selected_challenge_key}"
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
                sol_path = os.path.join(physical_challenge_dir, sol_filename)
                if os.path.exists(sol_path):
                    with open(sol_path, "r", encoding="utf-8") as f:
                        st.markdown(f.read())
                else:
                    st.info("No written solution guide available.")
