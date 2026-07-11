# AI Resume Intelligence Platform

<div align="center">
  <h1>🤖 AI Resume Intelligence Platform</h1>
  <p><strong>Production-ready multi-agent AI platform for semantic resume analysis, ATS scoring, and interview preparation</strong></p>
  
  [![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
  [![LangGraph](https://img.shields.io/badge/LangGraph-0.1-orange)](https://langgraph.readthedocs.io)
  [![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-purple)](https://docs.trychroma.com)
  [![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)](https://streamlit.io)
  [![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
  [![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
</div>

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG Semantic Matching** | ChromaDB + MiniLM embeddings for deep resume-JD matching |
| 📄 **OCR Support** | Tesseract for scanned PDF/image resumes |
| 🤖 **Multi-Agent Pipeline** | LangGraph orchestration with 8 specialized agents |
| 📊 **ATS Scoring** | Explainable 5-dimension score breakdown |
| ✍️ **STAR Rewriting** | AI-powered resume improvement using STAR methodology |
| 🎯 **Skill Gap Analysis** | Missing skill detection with learning recommendations |
| 🎤 **Interview Prep** | Personalized behavioral, technical, and situational questions |
| 👔 **Recruiter Dashboard** | Multi-candidate comparison and analytics |
| 📑 **PDF Reports** | Downloadable professional analysis reports |
| 🔐 **Role-Based Auth** | JWT with Recruiter/Candidate roles |
| 📚 **Swagger API** | Full REST API with OpenAPI documentation |
| 🐳 **Docker Ready** | Docker Compose for easy deployment |
| 🔄 **CI/CD** | GitHub Actions workflow |

---

## 🏗️ Architecture

```
                          ┌─────────────────────────────────────────────┐
                          │         LangGraph Multi-Agent Pipeline       │
                          │                                               │
  PDF/DOCX/Image  ──────► │  [Parser] → [JD] → [Embed] → [Score]        │
                          │                                               │
                          │  → [SkillGap] → [Rewrite] → [Interview]      │
                          │                                               │
                          │  → [Report Agent] → PDF Report               │
                          └─────────────┬───────────────────────────────┘
                                        │
                          ┌─────────────▼───────────────────────────────┐
                          │              FastAPI Backend                  │
                          │    REST API │ JWT Auth │ PostgreSQL           │
                          └─────────────┬───────────────────────────────┘
                                        │
                          ┌─────────────▼───────────────────────────────┐
                          │            Streamlit Frontend                 │
                          │  Candidate Dashboard │ Recruiter Dashboard    │
                          └─────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed
- HuggingFace API key (free at huggingface.co)

### 1. Clone & Setup

```bash
git clone https://github.com/yourname/resume-ai.git
cd resume-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your HuggingFace API key:
# HUGGINGFACE_API_KEY=hf_your_key_here
```

### 3. Run with Docker (Recommended)

```bash
docker-compose up --build
```

Access:
- 🌐 Frontend: http://localhost:8501
- 📚 API Docs: http://localhost:8000/docs

### 4. Run Locally (Development)

```bash
# Terminal 1 — Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — Frontend
streamlit run frontend/streamlit_app.py
```

---

## 📁 Project Structure

```
resume-ai/
├── frontend/                    # Streamlit UI
│   ├── streamlit_app.py         # Main app with auth
│   ├── pages/
│   │   ├── 01_candidate_dashboard.py   # Upload, analyze, results
│   │   ├── 02_recruiter_dashboard.py   # Job mgmt, candidate compare
│   │   ├── 04_interview_prep.py        # Interview Q&A
│   └── components/
│
├── backend/                     # FastAPI REST API
│   ├── main.py                  # App entry point
│   ├── api/                     # Route handlers
│   │   ├── auth.py              # JWT auth (register/login/me)
│   │   ├── resume.py            # Resume CRUD + upload
│   │   ├── jobs.py              # Job description CRUD
│   │   ├── analysis.py          # Pipeline trigger + results
│   │   └── reports.py           # PDF download
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── middleware/              # Logging middleware
│   ├── db/                      # Database setup
│   └── core/                    # Config settings
│
├── ai_engine/                   # AI/ML Core
│   ├── orchestrator/
│   │   └── langgraph_flow.py    # LangGraph pipeline
│   ├── agents/                  # 8 specialized agents
│   │   ├── parser_agent.py
│   │   ├── jd_agent.py
│   │   ├── retrieval_agent.py
│   │   ├── scoring_agent.py
│   │   ├── skill_gap_agent.py
│   │   ├── rewrite_agent.py
│   │   ├── interview_agent.py
│   │   └── report_agent.py
│   ├── llm/llm_factory.py       # HF/OpenAI/Gemini abstraction
│   ├── embeddings/embedder.py   # MiniLM-L6-v2 embeddings
│   ├── ocr/ocr_engine.py        # Tesseract OCR
│   ├── parser/resume_parser.py  # Multi-format parser
│   ├── rag/retriever.py         # ChromaDB RAG
│   ├── evaluation/ats_scorer.py # 5-dim ATS scorer
│   ├── recommendation/          # Skill recommendations
│   ├── prompts/                 # LLM prompt templates
│   └── report/pdf_generator.py  # ReportLab PDF
│
├── tests/                       # Pytest test suite
├── docker/                      # Dockerfiles
├── .github/workflows/ci.yml     # GitHub Actions CI/CD
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🤖 AI Models Used

| Component | Model | Provider | Cost |
|-----------|-------|----------|------|
| Text Generation | `mistralai/Mistral-7B-Instruct-v0.2` | HuggingFace API | Free tier |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` | Local (no API) | Free |
| OCR | Tesseract 5.x | Local | Free |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login & get JWT |
| GET | `/api/auth/me` | Current user profile |
| POST | `/api/resume/upload` | Upload resume |
| GET | `/api/resume/` | List resumes |
| GET | `/api/resume/{id}/parsed` | Get parsed data |
| POST | `/api/jobs/` | Create job description |
| GET | `/api/jobs/` | List jobs |
| POST | `/api/analysis/run` | Trigger analysis pipeline |
| GET | `/api/analysis/result/{rid}/{jid}` | Get analysis results |
| GET | `/api/analysis/recruiter/compare` | Compare candidates |
| POST | `/api/reports/{id}/generate` | Generate PDF report |
| GET | `/api/reports/{id}/download` | Download PDF |

Full Swagger docs at: **http://localhost:8000/docs**

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=backend --cov=ai_engine --cov-report=html

# Specific test file
pytest tests/test_scoring.py -v
```

---

## 🌐 Deployment

### AWS/Azure/Render

1. Push to GitHub
2. CI/CD runs automatically via GitHub Actions
3. Deploy with Docker Compose on your cloud VM

```bash
# On your server
git clone https://github.com/yourname/resume-ai.git
cd resume-ai
cp .env.example .env
# Fill in production values
docker-compose up -d
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) file.

---

<div align="center">
Built with ❤️ using FastAPI, LangGraph, ChromaDB, and Mistral-7B
</div>
