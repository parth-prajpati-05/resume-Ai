"""
All AI Agents for the Resume Intelligence Platform
Each agent is a focused, single-responsibility component
"""

# ── Parser Agent ──────────────────────────────────────────────────────────────
"""Parser Agent: Extracts structured data from resumes."""

import json
import re
from typing import Any, Dict
from loguru import logger

from ai_engine.parser.resume_parser import ResumeParser
from ai_engine.prompts.prompt_templates import RESUME_PARSE_PROMPT, JD_PARSE_PROMPT


class ParserAgent:
    """Responsible for parsing resumes into structured JSON."""

    def __init__(self, llm=None):
        self.parser = ResumeParser()
        self.llm = llm

    async def run(self, file_path: str, file_type: str) -> Dict[str, Any]:
        logger.info(f"[ParserAgent] Parsing resume: {file_path}")
        result = await self.parser.parse(file_path, file_type, self.llm)
        return result

    def parse_text(self, text: str) -> Dict[str, Any]:
        contact = self.parser.parse_with_rules(text)
        if self.llm:
            structured = self.parser.parse_with_llm(text, self.llm)
        else:
            structured = self.parser._fallback_section_parse(text)
        return {**contact, **structured, "raw_text": text}
