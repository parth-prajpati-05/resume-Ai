"""
LangGraph Multi-Agent Orchestration Flow
Coordinates all AI agents in a directed graph pipeline
"""

from typing import Any, Dict, Optional, TypedDict
from loguru import logger

from langgraph.graph import StateGraph, END

from ai_engine.llm.llm_factory import get_llm_factory
from ai_engine.agents.parser_agent import ParserAgent
from ai_engine.agents.jd_agent import JDAgent
from ai_engine.agents.retrieval_agent import RetrievalAgent
from ai_engine.agents.scoring_agent import ScoringAgent
from ai_engine.agents.skill_gap_agent import SkillGapAgent
from ai_engine.agents.rewrite_agent import RewriteAgent
from ai_engine.agents.interview_agent import InterviewAgent
from ai_engine.agents.report_agent import ReportAgent


# ── State Definition ──────────────────────────────────────────────────────────
class PipelineState(TypedDict):
    """Shared state across all agents in the LangGraph pipeline."""
    # Inputs
    file_path: Optional[str]
    file_type: Optional[str]
    resume_text: Optional[str]
    jd_text: Optional[str]
    resume_id: Optional[str]
    job_id: Optional[str]

    # Agent outputs
    resume_data: Optional[Dict]
    jd_data: Optional[Dict]
    embedding_id: Optional[str]
    ats_result: Optional[Dict]
    skill_gaps: Optional[Dict]
    rewritten_bullets: Optional[list]
    interview_questions: Optional[Dict]
    report_path: Optional[str]

    # Status
    error: Optional[str]
    stage: Optional[str]


class ResumeIntelligenceFlow:
    """
    Orchestrates the full multi-agent resume analysis pipeline using LangGraph.

    Pipeline graph:
    parse_resume → parse_jd → store_embeddings → score_ats
                → skill_gap → rewrite → interview → report → END
    """

    def __init__(self):
        self.llm_factory = get_llm_factory()
        self.llm = self.llm_factory.get_llm()

        # Instantiate agents
        self.parser_agent = ParserAgent(llm=self.llm_factory)
        self.jd_agent = JDAgent(llm=self.llm_factory)
        self.retrieval_agent = RetrievalAgent()
        self.scoring_agent = ScoringAgent()
        self.skill_gap_agent = SkillGapAgent(llm=self.llm_factory)
        self.rewrite_agent = RewriteAgent(llm=self.llm_factory)
        self.interview_agent = InterviewAgent(llm=self.llm_factory)
        self.report_agent = ReportAgent()

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Define the LangGraph state machine."""
        workflow = StateGraph(PipelineState)

        # Add nodes
        workflow.add_node("parse_resume", self._node_parse_resume)
        workflow.add_node("parse_jd", self._node_parse_jd)
        workflow.add_node("store_embeddings", self._node_store_embeddings)
        workflow.add_node("score_ats", self._node_score_ats)
        workflow.add_node("analyze_skill_gaps", self._node_skill_gaps)
        workflow.add_node("rewrite_resume", self._node_rewrite)
        workflow.add_node("generate_interview_q", self._node_interview)
        workflow.add_node("generate_report", self._node_report)

        # Define edges (linear pipeline)
        workflow.set_entry_point("parse_resume")
        workflow.add_edge("parse_resume", "parse_jd")
        workflow.add_edge("parse_jd", "store_embeddings")
        workflow.add_edge("store_embeddings", "score_ats")
        workflow.add_edge("score_ats", "analyze_skill_gaps")
        workflow.add_edge("analyze_skill_gaps", "rewrite_resume")
        workflow.add_edge("rewrite_resume", "generate_interview_q")
        workflow.add_edge("generate_interview_q", "generate_report")
        workflow.add_edge("generate_report", END)

        return workflow.compile()

    # ── Node Functions ─────────────────────────────────────────────────────────

    def _node_parse_resume(self, state: PipelineState) -> PipelineState:
        """Parse the resume file into structured data."""
        try:
            logger.info("📄 [Node] Parsing resume...")
            state["stage"] = "parsing_resume"
            
            if state.get("resume_text") and state.get("resume_data"):
                # Already parsed
                return state

            # Use text if provided, else parse from file
            if state.get("resume_text"):
                resume_data = self.parser_agent.parse_text(state["resume_text"])
            elif state.get("file_path"):
                import asyncio
                resume_data = asyncio.get_event_loop().run_until_complete(
                    self.parser_agent.run(state["file_path"], state.get("file_type", "pdf"))
                )
            else:
                resume_data = {}

            state["resume_data"] = resume_data
            if not state.get("resume_text"):
                state["resume_text"] = resume_data.get("raw_text", "")

        except Exception as e:
            logger.error(f"[Node parse_resume] Error: {e}")
            state["error"] = str(e)
            state["resume_data"] = {}
        return state

    def _node_parse_jd(self, state: PipelineState) -> PipelineState:
        """Parse the job description."""
        try:
            logger.info("📋 [Node] Parsing JD...")
            state["stage"] = "parsing_jd"

            if state.get("jd_data"):
                return state

            jd_text = state.get("jd_text", "")
            if jd_text:
                jd_data = self.jd_agent.run(jd_text)
                state["jd_data"] = jd_data
            else:
                state["jd_data"] = {}

        except Exception as e:
            logger.error(f"[Node parse_jd] Error: {e}")
            state["error"] = str(e)
            state["jd_data"] = {}
        return state

    def _node_store_embeddings(self, state: PipelineState) -> PipelineState:
        """Store resume and JD embeddings in ChromaDB."""
        try:
            logger.info("🗃️ [Node] Storing embeddings...")
            state["stage"] = "storing_embeddings"

            resume_id = state.get("resume_id", "temp")
            job_id = state.get("job_id", "temp")

            if state.get("resume_text") and state.get("resume_data"):
                embedding_id = self.retrieval_agent.store_resume(
                    resume_id, state["resume_data"], state["resume_text"]
                )
                state["embedding_id"] = embedding_id

            if state.get("jd_text") and state.get("jd_data"):
                self.retrieval_agent.store_jd(
                    job_id, state["jd_text"], state["jd_data"]
                )

        except Exception as e:
            logger.error(f"[Node store_embeddings] Error: {e}")
            state["error"] = str(e)
        return state

    def _node_score_ats(self, state: PipelineState) -> PipelineState:
        """Compute ATS score."""
        try:
            logger.info("🔢 [Node] Computing ATS score...")
            state["stage"] = "scoring"

            resume_text = state.get("resume_text", "")
            jd_text = state.get("jd_text", "")
            resume_data = state.get("resume_data", {})
            jd_data = state.get("jd_data", {})

            ats_result = self.scoring_agent.run(resume_text, jd_text, resume_data, jd_data)
            state["ats_result"] = ats_result

        except Exception as e:
            logger.error(f"[Node score_ats] Error: {e}")
            state["ats_result"] = {"total_score": 0.0, "breakdown": {}, "grade": "F"}
        return state

    def _node_skill_gaps(self, state: PipelineState) -> PipelineState:
        """Analyze skill gaps."""
        try:
            logger.info("🎯 [Node] Analyzing skill gaps...")
            state["stage"] = "skill_gap_analysis"

            resume_data = state.get("resume_data", {})
            jd_data = state.get("jd_data", {})

            resume_skills = resume_data.get("skills", [])
            required_skills = jd_data.get("required_skills", [])

            skill_gaps = self.skill_gap_agent.run(resume_skills, required_skills, jd_data)
            state["skill_gaps"] = skill_gaps

        except Exception as e:
            logger.error(f"[Node skill_gaps] Error: {e}")
            state["skill_gaps"] = {"missing_skills": [], "present_skills": [], "recommendations": []}
        return state

    def _node_rewrite(self, state: PipelineState) -> PipelineState:
        """Rewrite resume bullets using STAR methodology."""
        try:
            logger.info("✍️ [Node] Rewriting resume bullets...")
            state["stage"] = "rewriting"

            bullets = self.rewrite_agent.run(
                state.get("resume_data", {}),
                state.get("jd_data", {}),
            )
            state["rewritten_bullets"] = bullets

        except Exception as e:
            logger.error(f"[Node rewrite] Error: {e}")
            state["rewritten_bullets"] = []
        return state

    def _node_interview(self, state: PipelineState) -> PipelineState:
        """Generate interview questions."""
        try:
            logger.info("🎤 [Node] Generating interview questions...")
            state["stage"] = "interview_generation"

            questions = self.interview_agent.run(
                state.get("resume_data", {}),
                state.get("jd_data", {}),
            )
            state["interview_questions"] = questions

        except Exception as e:
            logger.error(f"[Node interview] Error: {e}")
            state["interview_questions"] = {}
        return state

    def _node_report(self, state: PipelineState) -> PipelineState:
        """Generate PDF report."""
        try:
            logger.info("📊 [Node] Generating PDF report...")
            state["stage"] = "report_generation"

            ats_result = state.get("ats_result", {})
            import asyncio
            report_path = asyncio.get_event_loop().run_until_complete(
                self.report_agent.run(
                    resume_data=state.get("resume_data", {}),
                    ats_score=ats_result.get("total_score", 0.0),
                    ats_breakdown=ats_result,
                    skill_gaps=state.get("skill_gaps", {}),
                    rewritten_bullets=state.get("rewritten_bullets", []),
                    interview_questions=state.get("interview_questions", {}),
                    resume_id=state.get("resume_id", "unknown"),
                    job_id=state.get("job_id", "unknown"),
                )
            )
            state["report_path"] = report_path

        except Exception as e:
            logger.error(f"[Node report] Error: {e}")
            state["report_path"] = None
        return state

    # ── Public API ─────────────────────────────────────────────────────────────

    async def parse_resume(self, file_path: str, file_type: str) -> Dict:
        """Parse a single resume file and return structured data."""
        return await self.parser_agent.run(file_path, file_type)

    async def parse_jd(self, jd_text: str) -> Dict:
        """Parse a job description and return structured data."""
        return self.jd_agent.run(jd_text)

    async def embed_and_store(self, resume_id: str, resume_data: Dict) -> str:
        """Embed and store a resume in ChromaDB."""
        raw_text = resume_data.get("raw_text", "")
        return self.retrieval_agent.store_resume(resume_id, resume_data, raw_text)

    async def run_full_pipeline(
        self,
        resume_data: Dict,
        jd_data: Dict,
        resume_text: str,
        jd_text: str,
        resume_id: str = "temp",
        job_id: str = "temp",
    ) -> Dict:
        """Run the complete multi-agent analysis pipeline."""
        logger.info(f"🚀 Running full LangGraph pipeline for resume={resume_id}")

        initial_state: PipelineState = {
            "file_path": None,
            "file_type": None,
            "resume_text": resume_text,
            "jd_text": jd_text,
            "resume_id": resume_id,
            "job_id": job_id,
            "resume_data": resume_data,
            "jd_data": jd_data,
            "embedding_id": None,
            "ats_result": None,
            "skill_gaps": None,
            "rewritten_bullets": None,
            "interview_questions": None,
            "report_path": None,
            "error": None,
            "stage": "init",
        }

        final_state = self.graph.invoke(initial_state)

        ats_result = final_state.get("ats_result", {})
        return {
            "ats_score": ats_result.get("total_score", 0.0),
            "ats_breakdown": ats_result,
            "skill_gaps": final_state.get("skill_gaps", {}),
            "rewritten_bullets": final_state.get("rewritten_bullets", []),
            "interview_questions": final_state.get("interview_questions", {}),
            "report_path": final_state.get("report_path"),
            "error": final_state.get("error"),
        }
