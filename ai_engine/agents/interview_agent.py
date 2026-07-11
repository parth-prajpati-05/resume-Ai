"""
Interview Question Generation Agent
Generates personalized behavioral, technical, and situational questions
"""

import json
import re
from typing import Dict, List
from loguru import logger

from ai_engine.prompts.prompt_templates import INTERVIEW_QUESTIONS_PROMPT


class InterviewAgent:
    """Generates personalized interview questions based on resume + JD."""

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, resume_data: dict, jd_data: dict) -> Dict:
        logger.info("[InterviewAgent] Generating interview questions...")

        if self.llm:
            return self._generate_with_llm(resume_data, jd_data)
        return self._generate_with_rules(resume_data, jd_data)

    def _generate_with_llm(self, resume_data: dict, jd_data: dict) -> Dict:
        job_title = jd_data.get("job_title", "Software Engineer")
        skills = resume_data.get("skills", [])[:10]
        experience = resume_data.get("experience", [])
        exp_summary = " | ".join(
            f"{e.get('company', '')} - {e.get('role', '')}"
            for e in experience[:3]
            if isinstance(e, dict)
        )

        prompt = INTERVIEW_QUESTIONS_PROMPT.format(
            job_title=job_title,
            candidate_skills=", ".join(skills),
            experience_summary=exp_summary or "Not specified",
        )
        response = self.llm.invoke(prompt)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.warning(f"LLM interview parse failed: {e}")

        return self._generate_with_rules(resume_data, jd_data)

    def _generate_with_rules(self, resume_data: dict, jd_data: dict) -> Dict:
        """Template-based interview question generation."""
        job_title = jd_data.get("job_title", "this role")
        skills = resume_data.get("skills", [])
        top_skill = skills[0] if skills else "programming"

        return {
            "technical": [
                {
                    "question": f"Can you walk me through your experience with {top_skill}?",
                    "difficulty": "medium",
                    "hint": "Look for depth of knowledge and practical application",
                },
                {
                    "question": f"How would you design a scalable system for {job_title.lower()} tasks?",
                    "difficulty": "hard",
                    "hint": "Assess system design and architecture knowledge",
                },
                {
                    "question": "Explain the difference between REST and GraphQL. When would you use each?",
                    "difficulty": "medium",
                    "hint": "Look for understanding of API design trade-offs",
                },
            ],
            "behavioral": [
                {
                    "question": "Tell me about a time you had to debug a critical production issue under pressure.",
                    "star_guidance": "Structure answer: Situation → Task → Action (debugging steps) → Result (impact/resolution)",
                },
                {
                    "question": "Describe a project where you had to learn a new technology quickly.",
                    "star_guidance": "Show adaptability, learning speed, and self-driven growth",
                },
                {
                    "question": "Give an example of a time you improved a process or workflow.",
                    "star_guidance": "Highlight initiative, impact (metrics if possible), and collaboration",
                },
            ],
            "situational": [
                {
                    "question": "If you discovered a major security vulnerability in production, what would you do?",
                    "ideal_response_elements": ["Immediate containment", "Notify stakeholders", "Fix & test", "Post-mortem"],
                },
                {
                    "question": "How would you handle disagreement with a senior developer about a technical approach?",
                    "ideal_response_elements": ["Listen first", "Data-driven argument", "Escalate appropriately", "Accept outcome"],
                },
            ],
            "culture_fit": [
                {"question": "What does a good engineering culture look like to you?"},
                {"question": "How do you keep your technical skills current?"},
                {"question": f"Why are you interested in this {job_title} position?"},
            ],
        }
