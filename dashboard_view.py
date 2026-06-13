import streamlit as st
from questions_db import CHALLENGES_DB
from helpers import (
    clean_name,
    get_difficulty_badge,
    get_group_meta,
    collect_module_groups,
    module_display_names
)

def render_dashboard(initialized_map, all_group_data, total_challenges):
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
        m_groups = collect_module_groups(CHALLENGES_DB, m_key)
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
                            # Reset cascading selectboxes
                            if "module_selector" in st.session_state:
                                st.session_state.module_selector = m_key
                        st.rerun()
    
    st.markdown("---")
    
    # ─── FILTER BAR ───
    st.markdown("### 🔍 Search & Filter Challenges")
    
    col_s1, col_s2, col_s3, col_s4 = st.columns([5, 2, 2, 2])
    
    with col_s1:
        search_query = st.text_input("Search challenge name or description...", placeholder="Type e.g. Anagram, Linear, TinyURL...", key="dashboard_search_input")
    with col_s2:
        diff_filter = st.selectbox("Difficulty", options=["All", "Easy", "Medium", "Hard"])
    with col_s3:
        all_groups_list = sorted(all_group_data.keys())
        try:
            default_grp_idx = [0] + [i+1 for i, g in enumerate(all_groups_list) if g == st.session_state.selected_group]
            grp_index = default_grp_idx[-1] if st.session_state.selected_group != "All" else 0
        except ValueError:
            grp_index = 0
            
        group_filter = st.selectbox("Group", options=["All"] + all_groups_list, index=grp_index)
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
                    
                    # Update widget keys directly in session state
                    if "module_selector" in st.session_state:
                        st.session_state.module_selector = item["m_key"]
                    if "topic_selector" in st.session_state:
                        st.session_state.topic_selector = item["t_key"]
                    if "challenge_selector" in st.session_state:
                        st.session_state.challenge_selector = item["c_key"]
                    
                    st.rerun()
            st.markdown("<hr style='margin:4px 0; border-color:#1E293B;'/>", unsafe_allow_html=True)
