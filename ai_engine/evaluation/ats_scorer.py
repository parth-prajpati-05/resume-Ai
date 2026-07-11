"""
ATS Scorer — explainable ATS score breakdown
Combines keyword matching + semantic similarity + structural analysis
"""

import re
from typing import Dict, List, Tuple
from loguru import logger

from ai_engine.embeddings.embedder import get_embedder


class ATSScorer:
    """
    Produces an ATS score with detailed breakdown across 5 dimensions:
    1. Keyword Match (25%)
    2. Semantic Similarity (35%)
    3. Skills Coverage (20%)
    4. Format/Structure (10%)
    5. Experience Alignment (10%)
    """

    WEIGHTS = {
        "keyword_match": 0.25,
        "semantic_similarity": 0.35,
        "skills_coverage": 0.20,
        "format_score": 0.10,
        "experience_alignment": 0.10,
    }

    def __init__(self):
        self.embedder = get_embedder()

    def compute_keyword_match(self, resume_text: str, jd_text: str) -> Tuple[float, Dict]:
        """Extract and match keywords from JD in resume."""
        # Extract meaningful words from JD (4+ chars, not stopwords)
        stopwords = {"with", "have", "this", "that", "will", "from", "your", "their",
                     "they", "must", "able", "strong", "good", "work", "team", "using"}
        
        jd_words = set(re.findall(r'\b[a-zA-Z][a-zA-Z+#\.]{2,}\b', jd_text))
        jd_keywords = {w.lower() for w in jd_words if w.lower() not in stopwords and len(w) >= 4}
        
        resume_lower = resume_text.lower()
        matched = [kw for kw in jd_keywords if kw in resume_lower]
        missing = [kw for kw in jd_keywords if kw not in resume_lower]

        score = len(matched) / max(len(jd_keywords), 1)
        
        return min(score, 1.0), {
            "matched_keywords": matched[:20],
            "missing_keywords": missing[:20],
            "match_rate": round(score * 100, 1),
        }

    def compute_semantic_similarity(self, resume_text: str, jd_text: str) -> float:
        """Compute semantic embedding similarity."""
        # Truncate for efficiency
        r_text = resume_text[:1500]
        j_text = jd_text[:1500]
        score = self.embedder.similarity_score(r_text, j_text)
        return max(0.0, min(1.0, score))

    def compute_skills_coverage(self, resume_skills: List[str], required_skills: List[str]) -> Tuple[float, Dict]:
        """Check how many required skills are present in resume."""
        if not required_skills:
            return 0.7, {"present": [], "missing": [], "coverage": 70.0}

        resume_skills_lower = [s.lower() for s in resume_skills]
        present = []
        missing = []

        for skill in required_skills:
            if any(skill.lower() in rs for rs in resume_skills_lower):
                present.append(skill)
            else:
                missing.append(skill)

        coverage = len(present) / max(len(required_skills), 1)
        return coverage, {
            "present_skills": present,
            "missing_skills": missing,
            "coverage": round(coverage * 100, 1),
        }

    def compute_format_score(self, resume_text: str) -> Tuple[float, List[str]]:
        """Check resume for structural quality indicators."""
        score = 1.0
        issues = []
        
        checks = {
            "email": (r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", "Missing email address"),
            "phone": (r"[\+]?[\d\s\-\(\)]{10,}", "Missing phone number"),
            "length": None,  # handled separately
        }

        if not re.search(checks["email"][0], resume_text):
            score -= 0.2
            issues.append(checks["email"][1])

        if not re.search(checks["phone"][0], resume_text):
            score -= 0.1
            issues.append(checks["phone"][1])

        # Check length (too short or too long)
        words = len(resume_text.split())
        if words < 100:
            score -= 0.3
            issues.append("Resume appears too short (< 100 words)")
        elif words > 1500:
            issues.append("Resume may be too long (consider trimming)")

        # Check for sections
        sections = ["experience", "education", "skills", "project"]
        missing_sections = [s for s in sections if s not in resume_text.lower()]
        if missing_sections:
            score -= 0.1 * len(missing_sections)
            issues.append(f"Missing sections: {', '.join(missing_sections)}")

        return max(0.0, score), issues

    def compute_experience_alignment(self, resume_data: dict, jd_data: dict) -> Tuple[float, str]:
        """Check if candidate experience matches JD requirements."""
        experience = resume_data.get("experience", [])
        exp_required = jd_data.get("experience_required", "")

        if not experience:
            return 0.3, "No experience found in resume"

        years_in_resume = len(experience)  # Approximate: number of roles

        # Extract required years from JD
        year_match = re.search(r"(\d+)\+?\s*years?", exp_required, re.IGNORECASE)
        required_years = int(year_match.group(1)) if year_match else 2

        if years_in_resume >= required_years:
            return 1.0, f"✅ Experience meets requirement ({years_in_resume} roles)"
        elif years_in_resume >= required_years * 0.5:
            return 0.6, f"⚠️ Partial experience match ({years_in_resume}/{required_years} required)"
        else:
            return 0.3, f"❌ Insufficient experience ({years_in_resume} roles, {required_years}+ required)"

    def score(
        self,
        resume_text: str,
        jd_text: str,
        resume_data: dict,
        jd_data: dict,
    ) -> Dict:
        """
        Compute full ATS score with explainable breakdown.
        Returns dict with total_score and all component scores.
        """
        logger.info("🔢 Computing ATS score...")

        # 1. Keyword match
        kw_score, kw_details = self.compute_keyword_match(resume_text, jd_text)

        # 2. Semantic similarity
        sem_score = self.compute_semantic_similarity(resume_text, jd_text)

        # 3. Skills coverage
        required_skills = jd_data.get("required_skills", [])
        resume_skills = resume_data.get("skills", [])
        skills_score, skills_details = self.compute_skills_coverage(resume_skills, required_skills)

        # 4. Format score
        fmt_score, fmt_issues = self.compute_format_score(resume_text)

        # 5. Experience alignment
        exp_score, exp_note = self.compute_experience_alignment(resume_data, jd_data)

        # Weighted total
        total = (
            kw_score * self.WEIGHTS["keyword_match"] +
            sem_score * self.WEIGHTS["semantic_similarity"] +
            skills_score * self.WEIGHTS["skills_coverage"] +
            fmt_score * self.WEIGHTS["format_score"] +
            exp_score * self.WEIGHTS["experience_alignment"]
        )
        total_pct = round(total * 100, 1)

        logger.info(f"✅ ATS Score: {total_pct}/100")

        return {
            "total_score": total_pct,
            "breakdown": {
                "keyword_match": {
                    "score": round(kw_score * 100, 1),
                    "weight": 25,
                    "weighted_score": round(kw_score * 25, 1),
                    "details": kw_details,
                },
                "semantic_similarity": {
                    "score": round(sem_score * 100, 1),
                    "weight": 35,
                    "weighted_score": round(sem_score * 35, 1),
                },
                "skills_coverage": {
                    "score": round(skills_score * 100, 1),
                    "weight": 20,
                    "weighted_score": round(skills_score * 20, 1),
                    "details": skills_details,
                },
                "format_score": {
                    "score": round(fmt_score * 100, 1),
                    "weight": 10,
                    "weighted_score": round(fmt_score * 10, 1),
                    "issues": fmt_issues,
                },
                "experience_alignment": {
                    "score": round(exp_score * 100, 1),
                    "weight": 10,
                    "weighted_score": round(exp_score * 10, 1),
                    "note": exp_note,
                },
            },
            "grade": self._get_grade(total_pct),
            "recommendation": self._get_recommendation(total_pct),
        }

    def _get_grade(self, score: float) -> str:
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 55:
            return "C"
        elif score >= 40:
            return "D"
        return "F"

    def _get_recommendation(self, score: float) -> str:
        if score >= 85:
            return "🟢 Excellent match! Highly recommended for interview."
        elif score >= 70:
            return "🟡 Good match. Minor improvements recommended."
        elif score >= 55:
            return "🟠 Moderate match. Significant skill gaps to address."
        return "🔴 Poor match. Consider targeting different roles or upskilling."
