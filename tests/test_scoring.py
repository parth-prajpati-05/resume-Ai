"""
Tests for ATS Scorer
"""

import pytest
from ai_engine.evaluation.ats_scorer import ATSScorer


class TestATSScorer:
    """Tests for the ATS scoring engine."""

    def setup_method(self):
        self.scorer = ATSScorer()

    def test_keyword_match_basic(self, sample_resume_text, sample_jd_text):
        score, details = self.scorer.compute_keyword_match(sample_resume_text, sample_jd_text)
        assert 0.0 <= score <= 1.0
        assert "matched_keywords" in details
        assert "missing_keywords" in details
        assert isinstance(details["matched_keywords"], list)

    def test_keyword_match_perfect(self):
        text = "Python FastAPI Docker Kubernetes PostgreSQL"
        score, _ = self.scorer.compute_keyword_match(text, text)
        assert score > 0.8  # Very high for identical text

    def test_keyword_match_no_overlap(self):
        resume = "Java Spring Hibernate Oracle"
        jd = "Python FastAPI MongoDB Docker"
        score, _ = self.scorer.compute_keyword_match(resume, jd)
        assert score < 0.3

    def test_skills_coverage_full(self):
        resume_skills = ["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "AWS"]
        required_skills = ["Python", "FastAPI", "Docker"]
        score, details = self.scorer.compute_skills_coverage(resume_skills, required_skills)
        assert score == 1.0
        assert len(details["missing_skills"]) == 0

    def test_skills_coverage_partial(self):
        resume_skills = ["Python", "FastAPI"]
        required_skills = ["Python", "FastAPI", "Docker", "Kubernetes"]
        score, details = self.scorer.compute_skills_coverage(resume_skills, required_skills)
        assert score == 0.5
        assert len(details["missing_skills"]) == 2

    def test_skills_coverage_empty_required(self):
        score, _ = self.scorer.compute_skills_coverage(["Python"], [])
        assert score == 0.7  # Default for no requirements

    def test_format_score_good_resume(self, sample_resume_text):
        score, issues = self.scorer.compute_format_score(sample_resume_text)
        assert score > 0.7
        assert isinstance(issues, list)

    def test_format_score_poor_resume(self):
        score, issues = self.scorer.compute_format_score("Hello world")
        assert score < 0.8
        assert len(issues) > 0

    def test_full_ats_score(self, sample_resume_text, sample_jd_text, sample_resume_data, sample_jd_data):
        result = self.scorer.score(
            sample_resume_text, sample_jd_text, sample_resume_data, sample_jd_data
        )
        assert "total_score" in result
        assert "breakdown" in result
        assert "grade" in result
        assert "recommendation" in result
        assert 0 <= result["total_score"] <= 100

    def test_grade_assignment(self):
        assert self.scorer._get_grade(90) == "A"
        assert self.scorer._get_grade(75) == "B"
        assert self.scorer._get_grade(60) == "C"
        assert self.scorer._get_grade(45) == "D"
        assert self.scorer._get_grade(20) == "F"

    def test_score_weights_sum_to_100(self):
        total_weight = sum(self.scorer.WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.001
