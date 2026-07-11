"""
Tests for Resume Parser and OCR Engine
"""

import pytest
from ai_engine.parser.resume_parser import ResumeParser


class TestResumeParser:
    """Tests for the resume parser."""

    def setup_method(self):
        self.parser = ResumeParser()

    def test_extract_email(self):
        text = "John Doe\njohn.doe@example.com\n+1-555-123-4567"
        result = self.parser._extract_email(text)
        assert result == "john.doe@example.com"

    def test_extract_phone(self):
        text = "Contact: +1-555-123-4567"
        result = self.parser._extract_phone(text)
        assert result is not None
        assert "555" in result

    def test_extract_linkedin(self):
        text = "linkedin.com/in/johndoe123"
        result = self.parser._extract_linkedin(text)
        assert result == "linkedin.com/in/johndoe123"

    def test_extract_github(self):
        text = "github.com/johndoe"
        result = self.parser._extract_github(text)
        assert result == "github.com/johndoe"

    def test_extract_name(self, sample_resume_text):
        result = self.parser._extract_name(sample_resume_text)
        assert result is not None

    def test_parse_with_rules(self, sample_resume_text):
        result = self.parser.parse_with_rules(sample_resume_text)
        assert "email" in result
        assert result["email"] == "john.doe@example.com"
        assert "phone" in result

    def test_fallback_section_parse(self, sample_resume_text):
        result = self.parser._fallback_section_parse(sample_resume_text)
        assert "skills" in result
        assert isinstance(result["skills"], list)
        assert len(result["skills"]) > 0

    def test_skills_extraction(self, sample_resume_text):
        result = self.parser._fallback_section_parse(sample_resume_text)
        skills = result.get("skills", [])
        # Should detect Python from the text
        assert any("Python" in s for s in skills)

    def test_empty_text(self):
        result = self.parser.parse_with_rules("")
        assert result["email"] is None
        assert result["phone"] is None
