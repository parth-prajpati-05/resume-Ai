"""
Retrieval Agent — handles semantic search and similarity scoring via ChromaDB
"""

from typing import Dict, List, Optional
from loguru import logger

from ai_engine.rag.retriever import get_retriever


class RetrievalAgent:
    """
    Handles vector search and semantic matching between resumes and JDs.
    Uses ChromaDB with sentence-transformer embeddings.
    """

    def __init__(self):
        self.retriever = get_retriever()

    def store_resume(self, resume_id: str, resume_data: dict, resume_text: str) -> str:
        """Store resume embedding in ChromaDB."""
        logger.info(f"[RetrievalAgent] Storing resume {resume_id}")
        return self.retriever.store_resume(resume_id, resume_data, resume_text)

    def store_jd(self, job_id: str, jd_text: str, jd_data: dict) -> str:
        """Store JD embedding in ChromaDB."""
        logger.info(f"[RetrievalAgent] Storing JD {job_id}")
        return self.retriever.store_jd(job_id, jd_text, jd_data)

    def semantic_match(self, resume_text: str, jd_text: str) -> float:
        """Compute semantic match score between resume and JD."""
        score = self.retriever.semantic_match_score(resume_text, jd_text)
        logger.info(f"[RetrievalAgent] Semantic match score: {score:.3f}")
        return score

    def find_matching_candidates(self, jd_text: str, top_k: int = 5) -> List[Dict]:
        """Find top-k most similar resumes for a given JD."""
        return self.retriever.find_similar_resumes(jd_text, n_results=top_k)

    def get_stats(self) -> Dict:
        """Return ChromaDB collection statistics."""
        return self.retriever.get_collection_stats()
