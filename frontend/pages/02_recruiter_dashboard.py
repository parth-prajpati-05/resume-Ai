"""
Recruiter Dashboard — Compare multiple candidates, manage JDs, view analytics
"""

import streamlit as st
import httpx
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Recruiter Dashboard", page_icon="👔", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0F0E1A 0%, #1A1830 100%); }
.stButton > button { background: linear-gradient(135deg, #6366F1, #8B5CF6) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
.candidate-card { background: rgba(99, 102, 241, 0.08); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 16px; margin: 8px 0; transition: border-color 0.2s; }
.candidate-card:hover { border-color: rgba(99, 102, 241, 0.6); }
.rank-badge { background: linear-gradient(135deg, #6366F1, #8B5CF6); color: white; border-radius: 50%; width: 32px; height: 32px; display: inline-flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.9rem; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please login first.")
    st.stop()

if st.session_state.get("user_role") != "recruiter":
    st.error("🔒 This dashboard is for Recruiters only.")
    st.stop()


def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 1rem 0;'>
    <h1 style='background: linear-gradient(135deg, #818CF8, #C084FC); -webkit-background-clip: text;
               -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 800;'>
        👔 Recruiter Dashboard
    </h1>
    <p style='color: #9CA3AF;'>Manage job descriptions and compare candidates intelligently</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Job Management", "👥 Candidate Comparison", "📈 Analytics"])


# ── Tab 1: Job Management ──────────────────────────────────────────────────────
with tab1:
    st.subheader("📋 Manage Job Descriptions")
    
    with st.expander("➕ Create New Job Description", expanded=True):
        with st.form("create_jd_form"):
            col1, col2 = st.columns(2)
            with col1:
                jd_title = st.text_input("Job Title*", placeholder="e.g., Senior Python Engineer")
                jd_company = st.text_input("Company", placeholder="e.g., TechCorp Inc.")
            jd_desc = st.text_area("Job Description*", height=200, placeholder="Paste full job description...")
            
            submitted = st.form_submit_button("📝 Create Job", use_container_width=True)
            if submitted and jd_title and jd_desc:
                try:
                    resp = httpx.post(
                        f"{BACKEND_URL}/api/jobs/",
                        headers=api_headers(),
                        json={"title": jd_title, "company": jd_company, "description": jd_desc},
                        timeout=30,
                    )
                    if resp.status_code == 201:
                        st.success(f"✅ Job '{jd_title}' created! ID: `{resp.json()['id'][:8]}`")
                    else:
                        st.error("❌ Failed to create job")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    st.markdown("---")
    st.subheader("📁 Your Job Descriptions")
    
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/jobs/", headers=api_headers(), timeout=10)
        jobs = resp.json() if resp.status_code == 200 else []
        
        if jobs:
            for job in jobs:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.markdown(f"**{job['title']}** @ {job.get('company', 'N/A')}")
                with col2:
                    st.markdown(f"<span style='color: #6B7280; font-size: 0.85rem;'>`{job['id'][:8]}...`</span>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<span style='color: #10B981;'>● {job['status']}</span>", unsafe_allow_html=True)
                with col4:
                    if st.button("🎯 Compare", key=f"cmp_{job['id']}"):
                        st.session_state["compare_job_id"] = job["id"]
                        st.session_state["compare_job_title"] = job["title"]
                st.markdown("---")
        else:
            st.info("No job descriptions yet. Create one above!")
    except Exception as e:
        st.warning(f"Could not load jobs: {e}")


# ── Tab 2: Candidate Comparison ────────────────────────────────────────────────
with tab2:
    st.subheader("👥 Compare Candidates for a Job")
    
    compare_job_id = st.session_state.get("compare_job_id", "")
    compare_job_id = st.text_input("Job ID to compare for", value=compare_job_id)
    
    if st.button("🔍 Load Candidates", use_container_width=True):
        if compare_job_id:
            with st.spinner("Loading candidate comparisons..."):
                try:
                    resp = httpx.get(
                        f"{BACKEND_URL}/api/analysis/recruiter/compare?job_id={compare_job_id}",
                        headers=api_headers(),
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        st.session_state["comparison_data"] = resp.json()
                    else:
                        st.error("❌ Could not load candidates")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    comp_data = st.session_state.get("comparison_data")
    if comp_data and comp_data.get("candidates"):
        candidates = comp_data["candidates"]
        total = comp_data.get("total_candidates", len(candidates))
        
        st.markdown(f"**Found {total} candidates — ranked by ATS score**")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        scores = [c.get("ats_score", 0) for c in candidates if c.get("ats_score")]
        with col1:
            st.metric("Total Candidates", total)
        with col2:
            st.metric("Avg ATS Score", f"{sum(scores)/len(scores):.1f}" if scores else "N/A")
        with col3:
            top = max(scores) if scores else 0
            st.metric("Top Score", f"{top:.1f}")
        
        # Comparison chart
        if candidates:
            df = pd.DataFrame([{
                "Name": c.get("candidate_name", "Unknown"),
                "ATS Score": c.get("ats_score", 0),
                "Skills Count": len(c.get("top_skills", [])),
            } for c in candidates])
            
            fig = px.bar(
                df, x="Name", y="ATS Score",
                color="ATS Score",
                color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                title="Candidate ATS Score Comparison",
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                title_font_color='white',
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Ranked candidate cards
        for rank, c in enumerate(candidates, 1):
            score = c.get("ats_score", 0)
            grade_color = "#10B981" if score >= 70 else ("#F59E0B" if score >= 50 else "#EF4444")
            medal = "🥇" if rank == 1 else ("🥈" if rank == 2 else ("🥉" if rank == 3 else f"#{rank}"))
            
            st.markdown(f"""
            <div class='candidate-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <span style='font-size: 1.2rem;'>{medal}</span>
                        <strong style='color: white; margin-left: 8px;'>{c.get('candidate_name', 'Unknown')}</strong>
                        <span style='color: #6B7280; font-size: 0.85rem; margin-left: 8px;'>{c.get('email', '')}</span>
                    </div>
                    <div>
                        <span style='background: {grade_color}22; color: {grade_color}; border: 1px solid {grade_color}44;
                                    border-radius: 8px; padding: 4px 12px; font-weight: 700; font-size: 1.1rem;'>
                            {score:.1f}
                        </span>
                    </div>
                </div>
                <div style='margin-top: 8px;'>
                    {''.join([f'<span style="background: rgba(99,102,241,0.2); border-radius: 20px; padding: 3px 10px; margin: 2px; font-size: 0.78rem; color: #A5B4FC; display: inline-block;">{s}</span>' for s in c.get('top_skills', [])[:5]])}
                </div>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 3: Analytics ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("📈 Platform Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution donut
        if st.session_state.get("comparison_data"):
            candidates = st.session_state["comparison_data"]["candidates"]
            scores = [c.get("ats_score", 0) for c in candidates]
            
            excellent = len([s for s in scores if s >= 80])
            good = len([s for s in scores if 60 <= s < 80])
            fair = len([s for s in scores if 40 <= s < 60])
            poor = len([s for s in scores if s < 40])
            
            fig_donut = go.Figure(go.Pie(
                values=[excellent, good, fair, poor],
                labels=["Excellent (80+)", "Good (60-80)", "Fair (40-60)", "Poor (<40)"],
                hole=0.5,
                marker=dict(colors=["#10B981", "#6366F1", "#F59E0B", "#EF4444"]),
            ))
            fig_donut.update_layout(
                title="Candidate Score Distribution",
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                title_font_color='white',
                height=350,
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Load candidate comparison data first to see analytics.")
    
    with col2:
        st.markdown("""
        <div style='background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3);
                    border-radius: 12px; padding: 20px; height: 350px;'>
            <h4 style='color: #818CF8;'>📊 Platform Stats</h4>
            <div style='color: #D1D5DB; font-size: 0.9rem; line-height: 2;'>
                <p>🤖 <strong>AI Engine:</strong> Mistral-7B-Instruct</p>
                <p>🔤 <strong>Embeddings:</strong> MiniLM-L6-v2</p>
                <p>🗃️ <strong>Vector Store:</strong> ChromaDB</p>
                <p>🔗 <strong>Framework:</strong> LangGraph</p>
                <p>📊 <strong>ATS Dimensions:</strong> 5</p>
                <p>🎤 <strong>Interview Q Types:</strong> 4</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
