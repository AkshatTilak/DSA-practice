import streamlit as st
import google.generativeai as genai
import os
from helpers import clean_name, extract_starter_code, extract_solutions, parse_solutions

# ─────────────────────────────────────────────────
# GEMINI FUNCTION CALLING TOOLS
# ─────────────────────────────────────────────────

def get_question_details(module_key: str, topic_key: str, challenge_key: str) -> dict:
    """
    Retrieve details for a specific coding or design challenge, including its description,
    difficulty, categories (groups), starter code, and available solution approaches.
    
    Args:
        module_key: The module name (e.g., '01_DSA', '02_Data_Science_ML', '03_LLD', '04_HLD').
        topic_key: The topic folder name (e.g., 'arrays_and_hashing', 'transformers').
        challenge_key: The challenge folder/identifier (e.g., 'q01_two_sum').
        
    Returns:
        A dictionary containing the challenge's difficulty, groups, description, link,
        starter template, and solution approaches.
    """
    from questions_db import CHALLENGES_DB
    
    if module_key not in CHALLENGES_DB:
        return {"error": f"Module '{module_key}' not found. Available: {list(CHALLENGES_DB.keys())}"}
    if topic_key not in CHALLENGES_DB[module_key]:
        return {"error": f"Topic '{topic_key}' not found in module '{module_key}'. Available: {list(CHALLENGES_DB[module_key].keys())}"}
    if challenge_key not in CHALLENGES_DB[module_key][topic_key]:
        return {"error": f"Challenge '{challenge_key}' not found in topic '{topic_key}'. Available: {list(CHALLENGES_DB[module_key][topic_key].keys())}"}

    info = CHALLENGES_DB[module_key][topic_key][challenge_key]
    
    # Resolve physical paths
    physical_challenge_dir = os.path.join(module_key, topic_key, challenge_key)
    physical_challenge_path = os.path.join(physical_challenge_dir, f"{challenge_key}.py")
    if not os.path.exists(physical_challenge_path):
        physical_challenge_path = os.path.join(physical_challenge_dir, f"{challenge_key}.md")
        
    starter_code = ""
    solutions = {}
    
    if os.path.exists(physical_challenge_path):
        if physical_challenge_path.endswith(".py"):
            starter_code = extract_starter_code(physical_challenge_path)
            raw_solutions = extract_solutions(physical_challenge_path)
            parsed_solutions_list = parse_solutions(raw_solutions)
            for title, content in parsed_solutions_list:
                solutions[title] = content
        else:
            try:
                with open(physical_challenge_path, "r", encoding="utf-8") as f:
                    starter_code = f.read()
            except Exception:
                pass
            
            sol_filename = f"{challenge_key}_solution.md"
            sol_path = os.path.join(physical_challenge_dir, sol_filename)
            if os.path.exists(sol_path):
                try:
                    with open(sol_path, "r", encoding="utf-8") as f:
                        solutions["Optimal Architecture"] = f.read()
                except Exception:
                    pass

    return {
        "module": module_key,
        "topic": topic_key,
        "challenge": challenge_key,
        "difficulty": info.get("difficulty", "Unknown"),
        "groups": info.get("groups", []),
        "description": info.get("description", ""),
        "link": info.get("link", ""),
        "starter_code": starter_code,
        "solution_approaches": list(solutions.keys())
    }

def get_questions_by_group(group_name: str) -> list:
    """
    Get a list of all available challenges in the study vault that belong to a specific group/category.
    
    Args:
        group_name: The name of the group/category (e.g., 'Array', 'String', 'Two Pointers', 'Tree', 'Transformers', 'Distributed Systems', etc.).
        
    Returns:
        A list of dictionaries containing challenge details (module, topic, challenge key, difficulty) matching the group.
    """
    from questions_db import CHALLENGES_DB
    
    matching_challenges = []
    for m in CHALLENGES_DB:
        for t in CHALLENGES_DB[m]:
            for c in CHALLENGES_DB[m][t]:
                info = CHALLENGES_DB[m][t][c]
                if group_name.lower() in [g.lower() for g in info.get("groups", [])]:
                    matching_challenges.append({
                        "module_key": m,
                        "topic_key": t,
                        "challenge_key": c,
                        "difficulty": info.get("difficulty", "Unknown"),
                        "groups": info.get("groups", [])
                    })
    return matching_challenges

def get_available_groups() -> list:
    """
    List all groups/categories available in the study system along with the count of challenges in each.
    
    Returns:
        A list of dictionaries, each containing the group name, count of challenges, and list of modules they belong to.
    """
    from questions_db import CHALLENGES_DB
    from helpers import collect_all_groups
    
    group_counts = collect_all_groups(CHALLENGES_DB)
    return [
        {
            "group_name": g,
            "count": data["total"],
            "modules": list(data["modules"])
        }
        for g, data in group_counts.items()
    ]

# ─────────────────────────────────────────────────
# SIDE PANEL AI COACH VIEW (NON-MODAL)
# ─────────────────────────────────────────────────

def render_ai_coach_panel(
    selected_module_key,
    selected_topic_key,
    selected_challenge_key,
    challenge_info,
    is_challenge_active,
    api_key,
    selected_model,
    current_view
):
    # Panel Header card
    if current_view == "Practice Sandbox":
        subtitle_text = f"Answering: {clean_name(selected_challenge_key)}"
    else:
        subtitle_text = "Browsing Explore Dashboard"

    st.markdown(f"""
    <div style='background-color: #111827; border: 1px solid #1E293B; border-radius: 12px; padding: 15px; margin-bottom: 12px;'>
        <div style='font-size: 1.1rem; font-weight: 600; color: #F8FAFC;'>💬 AI Study Coach</div>
        <p style='font-size: 0.78rem; color: #94A3B8; margin: 4px 0 0 0;'>
            {subtitle_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Close button in panel
    if st.button("❌ Close Coach", key="close_coach_panel_btn", use_container_width=True):
        st.session_state.show_ai_coach = False
        st.rerun()

    # Error check for Gemini API key
    if not api_key:
        st.warning("⚠️ **Gemini API Key Required**\nPlease enter your API key in the sidebar settings or define it as `API_KEY` in your `.env` file.")
        return

    # Scrollable chat messages container
    chat_container = st.container(height=420)
    with chat_container:
        if not st.session_state.chat_history:
            welcome_msg = (
                "Hello! I am your AI Study Coach. 🧠\n\n"
                "I can help you with coding challenges, design patterns, systems scaling, or ML concepts.\n\n"
            )
            if current_view == "Practice Sandbox":
                welcome_msg += f"Currently, you are looking at **{clean_name(selected_challenge_key)}**. Ask me for a hint, complexity analysis, or conceptual guide!"
            else:
                welcome_msg += "Ask me any concept explanation, search for challenges by group, or list available groups to start!"
            st.chat_message("assistant").write(welcome_msg)
        
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Chat Input Field
    if user_message := st.chat_input("Ask a hint, search groups...", key="panel_chat_input"):
        with chat_container:
            with st.chat_message("user"):
                st.write(user_message)
        st.session_state.chat_history.append({"role": "user", "content": user_message})

        # Dynamic System Instructions
        if current_view == "Practice Sandbox" and challenge_info:
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
5. You have tools to search the system database for other questions, details, and groups. Use them if the user asks.
"""
        else:
            system_prompt = """You are an elite Staff AI Engineer and Technical Interviewer.
You are helping the user study for technical coding/systems engineering loops.
Currently, they are browsing the Explore Dashboard and not active on a specific sandbox challenge.

Guidelines:
1. Act as a professional tutor. Suggest topics and help them select challenges to work on.
2. Recommend questions or groups based on their queries. Use your tools to list groups or search questions.
3. Keep the tone professional, helpful, and concise.
4. You have tools to search the system database for other questions, details, and groups. Use them if the user asks.
"""

        # Send message to Gemini API with automatic tool execution
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=selected_model,
                system_instruction=system_prompt,
                tools=[get_question_details, get_questions_by_group, get_available_groups]
            )

            # Reconstruct text turn history for the API
            gemini_history = []
            for h in st.session_state.chat_history[:-1]:
                gemini_history.append({
                    "role": "model" if h["role"] == "assistant" else h["role"],
                    "parts": [h["content"]]
                })

            with st.spinner("AI thinking..."):
                chat = model.start_chat(history=gemini_history, enable_automatic_function_calling=True)
                response = chat.send_message(user_message)
                ai_response = response.text

            with chat_container:
                with st.chat_message("assistant"):
                    st.write(ai_response)

            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.rerun()

        except Exception as e:
            st.error(f"Failed to communicate with Gemini API: {str(e)}")
            st.warning("Hint: If you hit a 404/model not found error, try changing the model selection in the sidebar.")
