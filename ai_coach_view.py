import streamlit as st
import google.generativeai as genai
import os

@st.dialog("💬 AI Study Coach", width="large")
def render_ai_coach_dialog(
    selected_module_key,
    selected_topic_key,
    selected_challenge_key,
    challenge_info,
    is_challenge_active,
    api_key,
    selected_model
):
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

    chat_container = st.container(height=350)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    if user_message := st.chat_input("Ask a hint or clarify concept...", key="dialog_chat_input"):
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
            st.rerun()
            
        except Exception as e:
            st.error(f"Failed to communicate with Gemini API: {str(e)}")
            st.warning("Hint: If you hit a 404 model not found error, try changing the Gemini Model selection in the sidebar.")

def render_ai_coach_button(
    selected_module_key,
    selected_topic_key,
    selected_challenge_key,
    challenge_info,
    is_challenge_active,
    api_key,
    selected_model
):
    if not api_key:
        return
        
    # Floating Action Button (FAB) layout using HTML wrapper and styles
    st.markdown('<div class="floating-container">', unsafe_allow_html=True)
    if st.button("💬 Ask Coach", key="floating_ai_coach_btn"):
        render_ai_coach_dialog(
            selected_module_key,
            selected_topic_key,
            selected_challenge_key,
            challenge_info,
            is_challenge_active,
            api_key,
            selected_model
        )
    st.markdown('</div>', unsafe_allow_html=True)
