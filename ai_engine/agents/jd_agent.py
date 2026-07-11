"""
JD Analysis Agent — extracts structured data from job descriptions
"""

import json
import re
from typing import Dict, Any, List
from loguru import logger

from ai_engine.prompts.prompt_templates import JD_PARSE_PROMPT


class JDAgent:
    """Analyzes job descriptions and extracts structured requirements."""

    def __init__(self, llm=None):
        self.llm = llm

    def run(self, jd_text: str) -> Dict[str, Any]:
        logger.info("[JDAgent] Analyzing job description...")

        if self.llm:
            return self._parse_with_llm(jd_text)
        return self._rule_based_parse(jd_text)

    def _parse_with_llm(self, jd_text: str) -> Dict[str, Any]:
        prompt = JD_PARSE_PROMPT.format(jd_text=jd_text[:2000])
        response = self.llm.invoke(prompt)
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            logger.warning(f"LLM JD parse failed, using rules: {e}")
        return self._rule_based_parse(jd_text)

    def _rule_based_parse(self, jd_text: str) -> Dict[str, Any]:
        """Fallback rule-based JD extraction."""
        tech_skills = [
            "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C++", "C#",
            "React", "Angular", "Vue", "Node.js", "Django", "FastAPI", "Flask", "Spring",
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Terraform",
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "LangChain",
            "REST API", "GraphQL", "Microservices", "CI/CD", "Git", "Linux",
        ]

        text_lower = jd_text.lower()
        found_skills = [s for s in tech_skills if s.lower() in text_lower]

        # Extract years of experience
        exp_match = re.search(r"(\d+)\+?\s*(?:to\s*\d+)?\s*years?", jd_text, re.IGNORECASE)
        experience_required = exp_match.group(0) if exp_match else "Not specified"

        # Extract job title (usually first line or after "Position:" etc.)
        lines = [l.strip() for l in jd_text.split("\n") if l.strip()]
        job_title = lines[0] if lines else "Software Engineer"

        return {
            "job_title": job_title[:100],
            "required_skills": found_skills,
            "preferred_skills": [],
            "experience_required": experience_required,
            "education_required": "Bachelor's degree" if "bachelor" in text_lower else "Not specified",
            "responsibilities": [],
            "qualifications": [],
        }
