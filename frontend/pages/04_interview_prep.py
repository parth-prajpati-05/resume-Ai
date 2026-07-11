"""
Interview Preparation Page — View personalized questions with STAR guidance
"""

import streamlit as st
import os

st.set_page_config(page_title="Interview Prep", page_icon="🎤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0F0E1A 0%, #1A1830 100%); }
.stButton > button { background: linear-gradient(135deg, #6366F1, #8B5CF6) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
.q-card { background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 16px; margin: 8px 0; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please login first.")
    st.stop()

st.markdown("""
<div style='padding: 1rem 0;'>
    <h1 style='background: linear-gradient(135deg, #818CF8, #C084FC); -webkit-background-clip: text;
               -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 800;'>
        🎤 Interview Preparation
    </h1>
    <p style='color: #9CA3AF;'>Practice with AI-generated personalized interview questions</p>
</div>
""", unsafe_allow_html=True)

results = st.session_state.get("last_results")

if not results or results.get("status") != "complete":
    st.info("💡 Run an analysis from the Candidate Dashboard first to get personalized interview questions.")
    st.markdown("""
    <div style='background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3);
                border-radius: 12px; padding: 20px; margin-top: 20px;'>
        <h4 style='color: #818CF8;'>📌 How to get interview questions:</h4>
        <ol style='color: #D1D5DB; line-height: 2;'>
            <li>Go to <strong>Candidate Dashboard</strong></li>
            <li>Upload your resume</li>
            <li>Select a job and run analysis</li>
            <li>Return here to view personalized questions</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
else:
    questions = results.get("interview_questions", {})

    if isinstance(questions, dict):
        categories = {
            "technical": ("⚙️ Technical Questions", "#6366F1"),
            "behavioral": ("🧠 Behavioral Questions (STAR)", "#8B5CF6"),
            "situational": ("💡 Situational Questions", "#C084FC"),
            "culture_fit": ("🏢 Culture Fit Questions", "#F472B6"),
        }

        for key, (title, color) in categories.items():
            if key in questions and questions[key]:
                st.markdown(f"## {title}")
                for i, q in enumerate(questions[key], 1):
                    if isinstance(q, dict):
                        q_text = q.get("question", "")
                        difficulty = q.get("difficulty", "")
                        star_guide = q.get("star_guidance", "")
                        hint = q.get("hint", "")
                        ideal = q.get("ideal_response_elements", [])

                        diff_color = {"easy": "#10B981", "medium": "#F59E0B", "hard": "#EF4444"}.get(difficulty, "#6B7280")

                        st.markdown(f"""
                        <div class='q-card'>
                            <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                                <div style='flex: 1;'>
                                    <strong style='color: white;'>Q{i}. {q_text}</strong>
                                </div>
                                {'<span style="background: ' + diff_color + '22; color: ' + diff_color + '; border: 1px solid ' + diff_color + '44; border-radius: 6px; padding: 2px 8px; font-size: 0.75rem; white-space: nowrap; margin-left: 10px;">' + difficulty.upper() + '</span>' if difficulty else ''}
                            </div>
                        """, unsafe_allow_html=True)

                        if star_guide:
                            st.markdown(f"<p style='color: #A5B4FC; font-size: 0.85rem; margin-top: 8px;'>💡 <em>{star_guide}</em></p>", unsafe_allow_html=True)
                        if hint:
                            st.markdown(f"<p style='color: #9CA3AF; font-size: 0.82rem;'>🔍 Interviewer looks for: <em>{hint}</em></p>", unsafe_allow_html=True)
                        if ideal:
                            elements_html = " | ".join([f"<span style='color: #C084FC;'>{e}</span>" for e in ideal])
                            st.markdown(f"<p style='font-size: 0.82rem;'>✅ Key elements: {elements_html}</p>", unsafe_allow_html=True)

                        st.markdown("</div>", unsafe_allow_html=True)

        # Practice mode
        st.markdown("---")
        st.subheader("🎯 Practice Mode")
        st.info("💡 Tip: Use the STAR method — Situation, Task, Action, Result — for behavioral questions.")

        with st.expander("📝 STAR Method Guide"):
            st.markdown("""
            | Component | Description | Example |
            |-----------|-------------|---------|
            | **S**ituation | Set the context | "At my previous company, we faced a critical deadline..." |
            | **T**ask | What was your responsibility | "I was tasked with refactoring the legacy API..." |
            | **A**ction | What did you do | "I led a team of 3, implemented caching, reduced latency..." |
            | **R**esult | Quantified outcome | "Reduced response time by 60%, saving $50K/month" |
            """)
