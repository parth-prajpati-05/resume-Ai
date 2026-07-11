"""
Skill Gap Recommender — generates learning resources for missing skills
"""

from typing import List, Dict
from loguru import logger


# Curated learning resources database
LEARNING_RESOURCES = {
    "python": [
        {"title": "Python for Everybody", "platform": "Coursera", "url": "https://coursera.org/learn/python", "level": "beginner"},
        {"title": "Python Crash Course", "platform": "Book", "url": "https://nostarch.com/python-crash-course-3rd-edition", "level": "beginner"},
    ],
    "machine learning": [
        {"title": "ML Specialization", "platform": "Coursera/DeepLearning.AI", "url": "https://coursera.org/specializations/machine-learning-introduction", "level": "intermediate"},
        {"title": "Hands-On ML with Scikit-Learn", "platform": "Book/O'Reilly", "url": "https://oreilly.com", "level": "intermediate"},
    ],
    "deep learning": [
        {"title": "Deep Learning Specialization", "platform": "Coursera/DeepLearning.AI", "url": "https://coursera.org/specializations/deep-learning", "level": "advanced"},
        {"title": "Fast.ai Practical Deep Learning", "platform": "fast.ai", "url": "https://fast.ai", "level": "intermediate"},
    ],
    "docker": [
        {"title": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "url": "https://udemy.com", "level": "intermediate"},
        {"title": "Docker Getting Started", "platform": "Docker Docs", "url": "https://docs.docker.com/get-started/", "level": "beginner"},
    ],
    "kubernetes": [
        {"title": "Certified Kubernetes Administrator (CKA)", "platform": "Linux Foundation", "url": "https://training.linuxfoundation.org/certification/certified-kubernetes-administrator-cka/", "level": "advanced"},
    ],
    "aws": [
        {"title": "AWS Cloud Practitioner", "platform": "AWS Training", "url": "https://aws.amazon.com/training/", "level": "beginner"},
        {"title": "AWS Solutions Architect Associate", "platform": "A Cloud Guru", "url": "https://acloudguru.com", "level": "intermediate"},
    ],
    "fastapi": [
        {"title": "FastAPI Official Tutorial", "platform": "FastAPI Docs", "url": "https://fastapi.tiangolo.com/tutorial/", "level": "beginner"},
        {"title": "Building Python APIs with FastAPI", "platform": "YouTube/Patrick Loeber", "url": "https://youtube.com", "level": "beginner"},
    ],
    "react": [
        {"title": "React - The Complete Guide", "platform": "Udemy/Academind", "url": "https://udemy.com", "level": "intermediate"},
        {"title": "React Official Docs", "platform": "react.dev", "url": "https://react.dev/learn", "level": "beginner"},
    ],
    "sql": [
        {"title": "SQL for Data Analysis", "platform": "Mode Analytics", "url": "https://mode.com/sql-tutorial/", "level": "beginner"},
        {"title": "PostgreSQL Full Course", "platform": "YouTube/freeCodeCamp", "url": "https://youtube.com", "level": "beginner"},
    ],
    "langchain": [
        {"title": "LangChain Official Docs", "platform": "LangChain", "url": "https://docs.langchain.com", "level": "intermediate"},
        {"title": "LangChain for LLM App Dev", "platform": "DeepLearning.AI", "url": "https://deeplearning.ai", "level": "intermediate"},
    ],
    "default": [
        {"title": "Search on Coursera", "platform": "Coursera", "url": "https://coursera.org", "level": "any"},
        {"title": "Search on YouTube", "platform": "YouTube", "url": "https://youtube.com", "level": "any"},
        {"title": "Search on Udemy", "platform": "Udemy", "url": "https://udemy.com", "level": "any"},
    ],
}


class SkillRecommender:
    """Generates learning recommendations for missing skills."""

    def get_resources(self, skill: str) -> List[Dict]:
        """Get learning resources for a specific skill."""
        skill_lower = skill.lower()
        
        # Direct match
        if skill_lower in LEARNING_RESOURCES:
            return LEARNING_RESOURCES[skill_lower][:2]
        
        # Partial match
        for key in LEARNING_RESOURCES:
            if key in skill_lower or skill_lower in key:
                return LEARNING_RESOURCES[key][:2]
        
        # Generic resources
        return [
            {
                "title": f"Learn {skill} - Search on Coursera",
                "platform": "Coursera",
                "url": f"https://coursera.org/search?query={skill.replace(' ', '+')}",
                "level": "any",
            },
            {
                "title": f"Learn {skill} - Search on YouTube",
                "platform": "YouTube",
                "url": f"https://youtube.com/results?search_query=learn+{skill.replace(' ', '+')}",
                "level": "any",
            },
        ]

    def generate_recommendations(
        self,
        missing_skills: List[str],
        present_skills: List[str],
        jd_data: dict,
    ) -> Dict:
        """Generate full skill gap analysis with recommendations."""
        recommendations = []

        for skill in missing_skills[:10]:  # Cap at 10 recommendations
            resources = self.get_resources(skill)
            priority = self._get_priority(skill, jd_data)
            recommendations.append({
                "skill": skill,
                "priority": priority,
                "estimated_time": self._estimate_time(skill),
                "resources": resources,
            })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 2))

        return {
            "missing_skills": missing_skills,
            "present_skills": present_skills,
            "recommendations": recommendations,
            "total_gaps": len(missing_skills),
            "quick_wins": [r["skill"] for r in recommendations if r["priority"] == "high"][:3],
        }

    def _get_priority(self, skill: str, jd_data: dict) -> str:
        """Determine if a skill is high/medium/low priority based on JD."""
        required = [s.lower() for s in jd_data.get("required_skills", [])]
        preferred = [s.lower() for s in jd_data.get("preferred_skills", [])]

        if skill.lower() in required:
            return "high"
        elif skill.lower() in preferred:
            return "medium"
        return "low"

    def _estimate_time(self, skill: str) -> str:
        """Rough time estimate to learn a skill."""
        advanced_skills = {"kubernetes", "machine learning", "deep learning", "aws certified"}
        intermediate_skills = {"docker", "react", "fastapi", "langchain", "postgresql"}

        if skill.lower() in advanced_skills:
            return "3-6 months"
        elif skill.lower() in intermediate_skills:
            return "4-8 weeks"
        return "1-3 weeks"
