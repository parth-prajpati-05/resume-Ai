"""
Candidate Dashboard — Resume upload, analysis, and results
"""

import streamlit as st
import httpx
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Candidate Dashboard", page_icon="👤", layout="wide")

# Inject shared CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.stApp { background: linear-gradient(135deg, #0F0E1A 0%, #1A1830 100%); }
.stButton > button { background: linear-gradient(135deg, #6366F1, #8B5CF6) !important; color: white !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important; }
.skill-tag { background: rgba(99, 102, 241, 0.2); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 20px; padding: 4px 12px; display: inline-block; margin: 3px; color: #A5B4FC; font-size: 0.82rem; }
.missing-tag { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 20px; padding: 4px 12px; display: inline-block; margin: 3px; color: #FCA5A5; font-size: 0.82rem; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please login first from the main page.")
    st.stop()


def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ── Page Header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 1rem 0;'>
    <h1 style='background: linear-gradient(135deg, #818CF8, #C084FC); -webkit-background-clip: text;
               -webkit-text-fill-color: transparent; font-size: 2rem; font-weight: 800;'>
        👤 Candidate Dashboard
    </h1>
    <p style='color: #9CA3AF;'>Upload your resume, match against jobs, and get AI-powered insights</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Upload Resume",
    "🎯 Analyze vs Job",
    "📊 My Results",
    "📑 Download Report",
])


# ── Tab 1: Upload Resume ───────────────────────────────────────────────────────
with tab1:
    st.subheader("Upload Your Resume")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_file = st.file_uploader(
            "Drop your resume here",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg"],
            help="Supported: PDF, DOCX, DOC, PNG, JPG, JPEG (OCR for scanned resumes)",
        )
        
        if uploaded_file:
            st.markdown(f"""
            <div style='background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3);
                        border-radius: 12px; padding: 12px; margin: 10px 0;'>
                <span style='color: #10B981;'>✅ {uploaded_file.name}</span><br>
                <span style='color: #6B7280; font-size: 0.8rem;'>{uploaded_file.size // 1024} KB</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Upload & Parse Resume", use_container_width=True):
                with st.spinner("📄 Uploading and parsing resume..."):
                    try:
                        resp = httpx.post(
                            f"{BACKEND_URL}/api/resume/upload",
                            headers=api_headers(),
                            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                            timeout=60,
                        )
                        if resp.status_code == 201:
                            data = resp.json()
                            st.session_state["resume_id"] = data["id"]
                            st.success(f"✅ Resume uploaded! ID: `{data['id'][:8]}...`")
                            st.info("⏳ Parsing in background. Check 'My Results' tab in 10-15 seconds.")
                        else:
                            st.error(f"❌ Upload failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
    
    with col2:
        st.markdown("""
        <div style='background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3);
                    border-radius: 12px; padding: 20px;'>
            <h4 style='color: #818CF8; margin-top: 0;'>📌 What happens when you upload?</h4>
            <ol style='color: #D1D5DB; font-size: 0.9rem; line-height: 1.8;'>
                <li>OCR text extraction (scanned PDFs supported)</li>
                <li>Structured data extraction via AI</li>
                <li>Embedding generation (MiniLM-L6-v2)</li>
                <li>Storage in ChromaDB for semantic search</li>
                <li>Ready for ATS analysis</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    # Show existing resumes
    st.markdown("---")
    st.subheader("📁 My Resumes")
    try:
        resp = httpx.get(f"{BACKEND_URL}/api/resume/", headers=api_headers(), timeout=10)
        if resp.status_code == 200:
            resumes = resp.json()
            if resumes:
                for r in resumes:
                    status_color = {"processed": "#10B981", "processing": "#F59E0B", "failed": "#EF4444"}.get(r["status"], "#6B7280")
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"📄 **{r['filename']}** — `{r['id'][:8]}...`")
                    with col2:
                        st.markdown(f"<span style='color: {status_color};'>● {r['status']}</span>", unsafe_allow_html=True)
                    with col3:
                        if st.button("Use This", key=f"use_{r['id']}"):
                            st.session_state["resume_id"] = r["id"]
                            st.success(f"✅ Selected resume {r['id'][:8]}")
            else:
                st.info("No resumes uploaded yet. Upload your first resume above!")
    except Exception as e:
        st.warning(f"Could not fetch resumes: {e}")


# ── Tab 2: Analyze vs Job ──────────────────────────────────────────────────────
with tab2:
    st.subheader("🎯 Match Resume Against Job Description")
    
    resume_id = st.session_state.get("resume_id", "")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_resume_id = st.text_input("Resume ID", value=resume_id, placeholder="Enter your resume ID...")
    with col2:
        # Fetch available jobs
        try:
            resp = httpx.get(f"{BACKEND_URL}/api/jobs/", headers=api_headers(), timeout=10)
            jobs = resp.json() if resp.status_code == 200 else []
            job_options = {f"{j['title']} ({j['id'][:8]})": j["id"] for j in jobs}
        except:
            jobs = []
            job_options = {}
        
        if job_options:
            selected_job_label = st.selectbox("Select Job", options=list(job_options.keys()))
            selected_job_id = job_options[selected_job_label]
        else:
            selected_job_id = st.text_input("Job ID", placeholder="Enter job ID or create a job first...")

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🔍 Run Full AI Analysis", use_container_width=True):
        if selected_resume_id and selected_job_id:
            with st.spinner("🤖 Running multi-agent AI pipeline... (may take 30-60 seconds)"):
                try:
                    resp = httpx.post(
                        f"{BACKEND_URL}/api/analysis/run",
                        headers=api_headers(),
                        json={"resume_id": selected_resume_id, "job_id": selected_job_id},
                        timeout=120,
                    )
                    if resp.status_code == 200:
                        st.session_state["analysis_job_id"] = selected_job_id
                        st.session_state["analysis_resume_id"] = selected_resume_id
                        st.success("✅ Analysis pipeline started! Go to 'My Results' tab to view.")
                    else:
                        st.error(f"❌ {resp.json().get('detail', 'Analysis failed')}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please select/enter both Resume ID and Job ID")

    st.markdown("---")
    st.subheader("➕ Or Paste a Job Description")
    
    jd_title = st.text_input("Job Title", placeholder="e.g., Senior Python Developer")
    jd_company = st.text_input("Company (optional)", placeholder="e.g., Google")
    jd_text = st.text_area("Job Description", height=200, placeholder="Paste the full job description here...")
    
    if st.button("📝 Create & Save Job", use_container_width=True):
        if jd_title and jd_text:
            try:
                resp = httpx.post(
                    f"{BACKEND_URL}/api/jobs/",
                    headers=api_headers(),
                    json={"title": jd_title, "company": jd_company, "description": jd_text},
                    timeout=30,
                )
                if resp.status_code == 201:
                    data = resp.json()
                    st.session_state["job_id"] = data["id"]
                    st.success(f"✅ Job saved! ID: `{data['id'][:8]}...`")
                else:
                    st.error("❌ Failed to save job description")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.warning("Please fill in Job Title and Description")


# ── Tab 3: My Results ──────────────────────────────────────────────────────────
with tab3:
    st.subheader("📊 Analysis Results")
    
    result_resume_id = st.session_state.get("analysis_resume_id", st.session_state.get("resume_id", ""))
    result_job_id = st.session_state.get("analysis_job_id", st.session_state.get("job_id", ""))
    
    col1, col2 = st.columns(2)
    with col1:
        result_resume_id = st.text_input("Resume ID for Results", value=result_resume_id)
    with col2:
        result_job_id = st.text_input("Job ID for Results", value=result_job_id)
    
    if st.button("🔄 Fetch Results"):
        if result_resume_id and result_job_id:
            with st.spinner("Fetching analysis results..."):
                try:
                    resp = httpx.get(
                        f"{BACKEND_URL}/api/analysis/result/{result_resume_id}/{result_job_id}",
                        headers=api_headers(),
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        results = resp.json()
                        st.session_state["last_results"] = results
                    else:
                        st.error("❌ Could not fetch results")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

    # Display results
    results = st.session_state.get("last_results")
    if results and results.get("status") == "complete":
        import plotly.graph_objects as go

        ats_score = results.get("ats_score", 0)
        breakdown = results.get("ats_breakdown", {}).get("breakdown", {})
        skill_gaps = results.get("skill_gaps", {})
        rewritten = results.get("rewritten_bullets", [])
        interview_q = results.get("interview_questions", {})

        # ATS Score Gauge
        st.markdown("---")
        st.markdown("### 🎯 ATS Score")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=ats_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "ATS Score", 'font': {'color': 'white', 'size': 18}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': 'gray'},
                    'bar': {'color': '#6366F1'},
                    'bgcolor': '#1E1B4B',
                    'steps': [
                        {'range': [0, 40], 'color': 'rgba(239,68,68,0.3)'},
                        {'range': [40, 70], 'color': 'rgba(245,158,11,0.3)'},
                        {'range': [70, 100], 'color': 'rgba(16,185,129,0.3)'},
                    ],
                    'threshold': {'line': {'color': '#818CF8', 'width': 4}, 'thickness': 0.75, 'value': ats_score},
                },
                number={'font': {'color': '#818CF8', 'size': 40}, 'suffix': '/100'},
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': 'white'},
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Breakdown radar chart
        if breakdown:
            st.markdown("### 📈 Score Breakdown")
            
            dims = list(breakdown.keys())
            scores = [breakdown[d].get("score", 0) for d in dims]
            dim_labels = [d.replace("_", " ").title() for d in dims]
            
            col1, col2 = st.columns(2)
            with col1:
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=scores + [scores[0]],
                    theta=dim_labels + [dim_labels[0]],
                    fill='toself',
                    fillcolor='rgba(99, 102, 241, 0.2)',
                    line=dict(color='#6366F1', width=2),
                    name='Your Score',
                ))
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 100], color='gray'),
                        angularaxis=dict(color='white'),
                        bgcolor='rgba(30, 27, 75, 0.5)',
                    ),
                    showlegend=False,
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    height=320,
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            with col2:
                fig_bar = go.Figure(go.Bar(
                    x=scores,
                    y=dim_labels,
                    orientation='h',
                    marker=dict(
                        color=scores,
                        colorscale=[[0, '#EF4444'], [0.5, '#F59E0B'], [1, '#10B981']],
                        showscale=False,
                    ),
                    text=[f"{s:.1f}%" for s in scores],
                    textposition='auto',
                ))
                fig_bar.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white'},
                    xaxis=dict(range=[0, 100], color='gray'),
                    yaxis=dict(color='white'),
                    height=320,
                    margin=dict(l=10, r=10, t=10, b=10),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

        # Skill Gaps
        if skill_gaps:
            st.markdown("### 🎯 Skill Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Matched Skills:**")
                present = skill_gaps.get("present_skills", [])
                if present:
                    tags = " ".join([f'<span class="skill-tag">✅ {s}</span>' for s in present[:15]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.info("No skills matched")
            
            with col2:
                st.markdown("**❌ Missing Skills:**")
                missing = skill_gaps.get("missing_skills", [])
                if missing:
                    tags = " ".join([f'<span class="missing-tag">❌ {s}</span>' for s in missing[:15]])
                    st.markdown(tags, unsafe_allow_html=True)
                else:
                    st.success("All required skills matched! 🎉")

        # STAR Rewritten Bullets
        if rewritten:
            st.markdown("### ✍️ STAR-Format Improvements")
            for i, bullet in enumerate(rewritten[:4], 1):
                if isinstance(bullet, dict):
                    with st.expander(f"Improvement #{i}: {bullet.get('original', '')[:60]}..."):
                        st.markdown(f"**Original:** {bullet.get('original', '')}")
                        st.markdown(f"**✨ Improved:** {bullet.get('rewritten', '')}")

        # Interview Questions
        if interview_q:
            st.markdown("### 🎤 Interview Questions")
            for category, questions in interview_q.items():
                if questions and isinstance(questions, list):
                    with st.expander(f"📌 {category.replace('_', ' ').title()} ({len(questions)} questions)"):
                        for q in questions:
                            q_text = q.get("question", str(q)) if isinstance(q, dict) else str(q)
                            st.markdown(f"• {q_text}")

    elif results and results.get("status") == "pending":
        st.info("⏳ Analysis still in progress. Please wait 30-60 seconds and refresh.")


# ── Tab 4: Download Report ─────────────────────────────────────────────────────
with tab4:
    st.subheader("📑 Download PDF Report")
    
    dl_resume_id = st.text_input("Resume ID", value=st.session_state.get("analysis_resume_id", ""))
    dl_job_id = st.text_input("Job ID", value=st.session_state.get("analysis_job_id", ""))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Generate Report", use_container_width=True):
            if dl_resume_id and dl_job_id:
                with st.spinner("Generating PDF report..."):
                    try:
                        resp = httpx.post(
                            f"{BACKEND_URL}/api/reports/{dl_resume_id}/generate?job_id={dl_job_id}",
                            headers=api_headers(),
                            timeout=30,
                        )
                        if resp.status_code == 200:
                            st.success("✅ Report generated!")
                        else:
                            st.error(f"❌ {resp.json().get('detail', 'Failed')}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    
    with col2:
        if st.button("⬇️ Download PDF", use_container_width=True):
            if dl_resume_id and dl_job_id:
                try:
                    resp = httpx.get(
                        f"{BACKEND_URL}/api/reports/{dl_resume_id}/download?job_id={dl_job_id}",
                        headers=api_headers(),
                        timeout=30,
                    )
                    if resp.status_code == 200:
                        st.download_button(
                            "💾 Save PDF",
                            data=resp.content,
                            file_name=f"resume_analysis_{dl_resume_id[:8]}.pdf",
                            mime="application/pdf",
                        )
                    else:
                        st.error("❌ Report not found. Generate it first.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
