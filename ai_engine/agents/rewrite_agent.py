"""
Resume Rewrite Agent — rewrites resume bullets using STAR methodology
"""

import json
import re
from typing import Dict, List
from loguru import logger

from ai_engine.prompts.prompt_templates import STAR_REWRITE_PROMPT


class RewriteAgent:
    """
    Rewrites resume bullet points using STAR methodology:
    Situation, Task, Action, Result
    """

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, resume_data: dict, jd_data: dict) -> List[Dict]:
        logger.info("[RewriteAgent] Rewriting bullets using STAR methodology...")

        experience = resume_data.get("experience", [])
        if not experience:
            logger.warning("[RewriteAgent] No experience found in resume")
            return []

        # Collect all bullets
        all_bullets = []
        for job in experience:
            if isinstance(job, dict):
                bullets = job.get("bullets", [])
                all_bullets.extend(bullets[:3])  # Max 3 per role

        if not all_bullets:
            return self._generate_sample_improvements(experience, jd_data)

        if self.llm:
            return self._rewrite_with_llm(all_bullets, jd_data)
        return self._rewrite_with_rules(all_bullets)

    def _rewrite_with_llm(self, bullets: List[str], jd_data: dict) -> List[Dict]:
        job_title = jd_data.get("job_title", "Software Engineer")
        bullets_text = "\n".join(f"- {b}" for b in bullets[:8])

        prompt = STAR_REWRITE_PROMPT.format(
            job_title=job_title,
            original_bullets=bullets_text,
        )
        response = self.llm.invoke(prompt)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return parsed.get("rewritten_bullets", [])
        except Exception as e:
            logger.warning(f"LLM rewrite parse failed: {e}")

        return self._rewrite_with_rules(bullets)

    def _rewrite_with_rules(self, bullets: List[str]) -> List[Dict]:
        """Simple rule-based improvement: add metrics and action verbs."""
        strong_verbs = [
            "Engineered", "Architected", "Optimized", "Implemented", "Delivered",
            "Reduced", "Increased", "Automated", "Led", "Designed", "Built", "Scaled",
        ]

        rewritten = []
        for i, bullet in enumerate(bullets[:6]):
            verb = strong_verbs[i % len(strong_verbs)]
            # Add stronger verb if sentence starts with weak word
            weak_starts = ["worked", "helped", "assisted", "did", "made", "was"]
            improved = bullet
            for weak in weak_starts:
                if bullet.lower().startswith(weak):
                    improved = f"{verb} {bullet[len(weak):].strip()}"
                    break

            # Suggest adding metrics
            if not any(c.isdigit() for c in improved):
                improved += " (consider adding measurable impact, e.g., improved performance by X%)"

            rewritten.append({
                "original": bullet,
                "rewritten": improved,
                "star_type": "action/result focused",
            })

        return rewritten

    def _generate_sample_improvements(self, experience: List, jd_data: dict) -> List[Dict]:
        """Generate sample improvement suggestions when no bullets found."""
        return [
            {
                "original": "No detailed bullet points found",
                "rewritten": "Add quantified bullet points like: 'Developed X feature that improved Y by Z%'",
                "star_type": "recommendation",
            }
        ]
