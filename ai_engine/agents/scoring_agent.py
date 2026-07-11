"""
Scoring Agent — computes the ATS score with explainable breakdown
"""

from typing import Dict
from loguru import logger

from ai_engine.evaluation.ats_scorer import ATSScorer


class ScoringAgent:
    """
    Computes the full ATS score with weighted breakdown.
    Dimensions: keyword match, semantic similarity, skills, format, experience.
    """

    def __init__(self):
        self.scorer = ATSScorer()

    def run(
        self,
        resume_text: str,
        jd_text: str,
        resume_data: dict,
        jd_data: dict,
    ) -> Dict:
        """Compute and return full ATS score with breakdown."""
        logger.info("[ScoringAgent] Computing ATS score...")
        result = self.scorer.score(resume_text, jd_text, resume_data, jd_data)
        logger.info(f"[ScoringAgent] ATS Score: {result['total_score']}/100 | Grade: {result['grade']}")
        return result
