"""
AI Resume Intelligence Platform — Main Streamlit Application
Premium dark-themed UI with analytics and visualizations
"""

import streamlit as st
import os

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Intelligence Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/resume-ai",
        "Report a bug": "https://github.com/resume-ai/issues",
        "About": "AI Resume Intelligence Platform v1.0",
    },
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    * { font-family: 'Inter', sans-serif !important; }
    
    .main { background: #0F0E1A; }
    .stApp { background: linear-gradient(135deg, #0F0E1A 0%, #1A1830 50%, #0D1117 100%); }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E1B4B 0%, #312E81 100%) !important;
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1E1B4B, #312E81);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(99, 102, 241, 0.2);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.35);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #9CA3AF;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.6) !important;
    }

    /* Upload area */
    .uploadedFile {
        background: rgba(99, 102, 241, 0.1) !important;
        border: 1px dashed rgba(99, 102, 241, 0.5) !important;
        border-radius: 12px !important;
    }

    /* Success/Error boxes */
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(5, 150, 105, 0.1));
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
    }
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.1));
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
    }
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.1));
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
    }

    /* Score gauge */
    .score-display {
        background: linear-gradient(135deg, #1E1B4B, #312E81);
        border-radius: 50%;
        width: 140px;
        height: 140px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        border: 3px solid rgba(99, 102, 241, 0.5);
        box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
    }
    
    /* Hero gradient text */
    .hero-title {
        background: linear-gradient(135deg, #818CF8, #C084FC, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.1;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #9CA3AF;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
        color: white !important;
    }

    /* Hide streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "token" not in st.session_state:
    st.session_state.token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


# ── Helper Functions ──────────────────────────────────────────────────────────
def api_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def show_hero():
    """Display the hero section."""
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div style='padding: 2rem 0;'>
            <div class='hero-title'>🤖 AI Resume<br>Intelligence Platform</div>
            <p style='color: #9CA3AF; font-size: 1.1rem; margin-top: 1rem;'>
                RAG-powered semantic matching • Multi-agent AI • ATS scoring<br>
                STAR rewriting • Interview prep • Professional PDF reports
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='padding: 2rem 1rem; text-align: center;'>
            <div style='font-size: 5rem;'>🧠</div>
            <p style='color: #818CF8; font-weight: 600;'>Powered by Mistral-7B + LangGraph</p>
        </div>
        """, unsafe_allow_html=True)


# ── Auth Forms ────────────────────────────────────────────────────────────────
def show_login_page():
    """Display login/register forms."""
    show_hero()
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Welcome back!")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submitted:
                if email and password:
                    import httpx
                    try:
                        resp = httpx.post(
                            f"{BACKEND_URL}/api/auth/login",
                            data={"username": email, "password": password},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.authenticated = True
                            st.session_state.token = data["access_token"]
                            st.session_state.user_role = data["role"]
                            st.session_state.user_id = data["user_id"]
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please try again.")
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
                else:
                    st.warning("Please enter email and password")

    with tab2:
        with st.form("register_form"):
            st.subheader("Create your account")
            col1, col2 = st.columns(2)
            with col1:
                reg_email = st.text_input("Email*", placeholder="you@example.com")
                reg_username = st.text_input("Username*")
            with col2:
                reg_name = st.text_input("Full Name")
                reg_role = st.selectbox("Role", ["candidate", "recruiter"])
            
            reg_password = st.text_input("Password*", type="password")
            reg_submitted = st.form_submit_button("✨ Create Account", use_container_width=True)
            
            if reg_submitted:
                if reg_email and reg_username and reg_password:
                    import httpx
                    try:
                        resp = httpx.post(
                            f"{BACKEND_URL}/api/auth/register",
                            json={
                                "email": reg_email,
                                "username": reg_username,
                                "password": reg_password,
                                "full_name": reg_name,
                                "role": reg_role,
                            },
                        )
                        if resp.status_code == 201:
                            st.success("🎉 Account created! Please login.")
                        else:
                            try:
                                detail = resp.json().get("detail", "Registration failed")
                            except Exception:
                                detail = f"Registration failed (HTTP {resp.status_code})"
                            st.error(f"❌ {detail}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <div style='font-size: 2.5rem;'>🤖</div>
            <div style='color: white; font-size: 1.1rem; font-weight: 700;'>Resume AI</div>
            <div style='color: #A5B4FC; font-size: 0.75rem;'>Intelligence Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        role_icon = "👔" if st.session_state.user_role == "recruiter" else "👤"
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.1); border-radius: 10px; padding: 12px; margin-bottom: 1rem;'>
            <div style='color: white; font-weight: 600;'>{role_icon} {st.session_state.username or 'User'}</div>
            <div style='color: #A5B4FC; font-size: 0.8rem; text-transform: capitalize;'>{st.session_state.user_role or ''}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        
        st.markdown("""
        <div style='color: #6B7280; font-size: 0.75rem; text-align: center; padding-top: 1rem;'>
            <p>Powered by</p>
            <p style='color: #818CF8;'>Mistral-7B • LangGraph</p>
            <p style='color: #818CF8;'>ChromaDB • FastAPI</p>
        </div>
        """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.authenticated:
        show_login_page()
    else:
        show_sidebar()
        
        # Welcome banner
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.1));
                    border: 1px solid rgba(99,102,241,0.3); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;'>
            <h2 style='color: #E0E7FF; margin: 0;'>
                👋 Welcome to AI Resume Intelligence
            </h2>
            <p style='color: #9CA3AF; margin: 0.5rem 0 0 0;'>
                Use the pages in the sidebar to upload resumes, run analysis, and download reports.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Quick stats row
        col1, col2, col3, col4 = st.columns(4)
        stats = [
            ("📄", "Resume Upload", "Upload & Parse"),
            ("🧠", "AI Analysis", "RAG + Semantic"),
            ("📊", "ATS Scoring", "5-Dimension"),
            ("📑", "PDF Reports", "Downloadable"),
        ]
        for col, (icon, title, subtitle) in zip([col1, col2, col3, col4], stats):
            with col:
                st.markdown(f"""
                <div class='metric-card'>
                    <div style='font-size: 2rem;'>{icon}</div>
                    <div style='color: white; font-weight: 600; margin-top: 8px;'>{title}</div>
                    <div class='metric-label'>{subtitle}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("📌 Navigate using the **sidebar pages** to access all features.")


if __name__ == "__main__":
    main()
