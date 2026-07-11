"""
Skill Gap Agent — identifies missing skills and generates learning recommendations
"""

import json
import re
from typing import Dict, List
from loguru import logger

from ai_engine.recommendation.skill_recommender import SkillRecommender
from ai_engine.prompts.prompt_templates import SKILL_GAP_PROMPT


class SkillGapAgent:
    """
    Analyzes the gap between resume skills and JD requirements.
    Produces prioritized learning recommendations.
    """

    def __init__(self, llm=None):
        self.recommender = SkillRecommender()
        self.llm = llm

    def run(
        self,
        resume_skills: List[str],
        required_skills: List[str],
        jd_data: dict,
    ) -> Dict:
        logger.info(f"[SkillGapAgent] Analyzing {len(required_skills)} required skills...")

        if self.llm and required_skills:
            result = self._analyze_with_llm(resume_skills, required_skills)
        else:
            result = self._analyze_with_rules(resume_skills, required_skills)

        # Enrich with learning recommendations
        enriched = self.recommender.generate_recommendations(
            missing_skills=result.get("missing_skills", []),
            present_skills=result.get("present_skills", []),
            jd_data=jd_data,
        )

        logger.info(
            f"[SkillGapAgent] Found {len(enriched['missing_skills'])} gaps, "
            f"{len(enriched['present_skills'])} matches"
        )
        return enriched

    def _analyze_with_llm(self, resume_skills: List[str], required_skills: List[str]) -> Dict:
        prompt = SKILL_GAP_PROMPT.format(
            candidate_skills=", ".join(resume_skills[:30]),
            required_skills=", ".join(required_skills[:30]),
        )
        response = self.llm.invoke(prompt)
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.warning(f"LLM skill gap parse failed: {e}")
        return self._analyze_with_rules(resume_skills, required_skills)

    def _analyze_with_rules(self, resume_skills: List[str], required_skills: List[str]) -> Dict:
        resume_lower = [s.lower() for s in resume_skills]
        present = [s for s in required_skills if s.lower() in resume_lower]
        missing = [s for s in required_skills if s.lower() not in resume_lower]
        return {
            "present_skills": present,
            "missing_skills": missing,
            "partial_skills": [],
            "overall_fit": "strong" if len(present) / max(len(required_skills), 1) > 0.7 else "moderate",
        }
