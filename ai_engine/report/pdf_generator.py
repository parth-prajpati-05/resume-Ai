"""
PDF Report Generator using ReportLab
Generates professional downloadable analysis reports
"""

import os
from datetime import datetime
from typing import Dict, List
from loguru import logger

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

from backend.core.config import settings


# ── Color Palette ─────────────────────────────────────────────────────────────
PRIMARY = HexColor("#6366F1")      # Indigo
SECONDARY = HexColor("#8B5CF6")    # Violet
SUCCESS = HexColor("#10B981")      # Green
WARNING = HexColor("#F59E0B")      # Amber
DANGER = HexColor("#EF4444")       # Red
DARK = HexColor("#1E1B4B")         # Dark Indigo
LIGHT = HexColor("#F8F7FF")        # Very Light Purple
GRAY = HexColor("#6B7280")
LIGHT_GRAY = HexColor("#F3F4F6")


class PDFReportGenerator:
    """
    Generates professional PDF analysis reports with:
    - Candidate summary
    - ATS score gauge
    - Breakdown table
    - Skill gap analysis
    - STAR rewritten bullets
    - Interview questions
    """

    def __init__(self):
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _setup_styles(self):
        """Define custom paragraph styles."""
        self.h1 = ParagraphStyle(
            "H1",
            parent=self.styles["Heading1"],
            fontSize=22,
            textColor=white,
            spaceAfter=6,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER,
        )
        self.h2 = ParagraphStyle(
            "H2",
            parent=self.styles["Heading2"],
            fontSize=14,
            textColor=PRIMARY,
            spaceAfter=8,
            spaceBefore=16,
            fontName="Helvetica-Bold",
        )
        self.body = ParagraphStyle(
            "Body",
            parent=self.styles["Normal"],
            fontSize=10,
            textColor=black,
            spaceAfter=4,
            fontName="Helvetica",
            leading=14,
        )
        self.small = ParagraphStyle(
            "Small",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=GRAY,
        )
        self.subtitle = ParagraphStyle(
            "Subtitle",
            parent=self.styles["Normal"],
            fontSize=11,
            textColor=LIGHT,
            alignment=TA_CENTER,
        )

    def _score_color(self, score: float) -> HexColor:
        if score >= 80:
            return SUCCESS
        elif score >= 60:
            return WARNING
        return DANGER

    def _build_header(self, candidate_name: str, job_title: str) -> list:
        """Build the report header section."""
        header_style = ParagraphStyle(
            "HeaderBG",
            parent=self.styles["Normal"],
            backColor=DARK,
            borderPadding=20,
        )

        # Header table with dark background
        header_data = [
            [Paragraph("🤖 AI Resume Intelligence Report", self.h1)],
            [Paragraph(f"Candidate: {candidate_name}", self.subtitle)],
            [Paragraph(f"Target Role: {job_title} | Generated: {datetime.now().strftime('%B %d, %Y')}", self.small)],
        ]
        header_table = Table(header_data, colWidths=[16 * cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), DARK),
            ("TEXTCOLOR", (0, 0), (-1, -1), white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 20),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
            ("LEFTPADDING", (0, 0), (-1, -1), 30),
            ("RIGHTPADDING", (0, 0), (-1, -1), 30),
            ("ROUNDEDCORNERS", [8, 8, 8, 8]),
        ]))
        return [header_table, Spacer(1, 0.5 * cm)]

    def _build_ats_score_section(self, ats_score: float, breakdown: dict) -> list:
        """Build ATS score summary section."""
        elements = [
            Paragraph("📊 ATS Score Analysis", self.h2),
            HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY),
            Spacer(1, 0.3 * cm),
        ]

        grade = breakdown.get("grade", "N/A") if isinstance(breakdown, dict) else "N/A"
        recommendation = breakdown.get("recommendation", "") if isinstance(breakdown, dict) else ""
        score_color = self._score_color(ats_score)

        # Score highlight box
        score_style = ParagraphStyle(
            "ScoreBox",
            parent=self.styles["Normal"],
            fontSize=36,
            fontName="Helvetica-Bold",
            textColor=score_color,
            alignment=TA_CENTER,
        )
        grade_style = ParagraphStyle(
            "Grade",
            parent=self.styles["Normal"],
            fontSize=18,
            fontName="Helvetica-Bold",
            textColor=score_color,
            alignment=TA_CENTER,
        )

        score_table = Table(
            [
                [Paragraph(f"{ats_score:.1f}", score_style), Paragraph(f"Grade: {grade}", grade_style)],
                [Paragraph("ATS Score", self.small), Paragraph("Overall Rating", self.small)],
            ],
            colWidths=[8 * cm, 8 * cm]
        )
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 15),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("BOX", (0, 0), (-1, -1), 1, LIGHT_GRAY),
            ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 0.3 * cm))

        if recommendation:
            elements.append(Paragraph(recommendation, self.body))

        return elements

    def _build_breakdown_table(self, breakdown: dict) -> list:
        """Build the ATS breakdown table."""
        elements = [
            Paragraph("📈 Score Breakdown", self.h2),
            HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY),
            Spacer(1, 0.3 * cm),
        ]

        bd = breakdown.get("breakdown", {}) if isinstance(breakdown, dict) else {}

        table_data = [
            ["Dimension", "Score", "Weight", "Weighted", "Status"],
        ]

        dimension_labels = {
            "keyword_match": "🔤 Keyword Match",
            "semantic_similarity": "🧠 Semantic Similarity",
            "skills_coverage": "⚡ Skills Coverage",
            "format_score": "📄 Format & Structure",
            "experience_alignment": "💼 Experience Alignment",
        }

        for key, label in dimension_labels.items():
            if key in bd:
                dim = bd[key]
                score = dim.get("score", 0)
                weight = dim.get("weight", 0)
                weighted = dim.get("weighted_score", 0)
                status = "✅" if score >= 70 else ("⚠️" if score >= 50 else "❌")
                table_data.append([
                    label,
                    f"{score:.1f}%",
                    f"{weight}%",
                    f"{weighted:.1f}",
                    status,
                ])

        table = Table(table_data, colWidths=[5.5 * cm, 2.5 * cm, 2 * cm, 2.5 * cm, 1.5 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        return elements

    def _build_skill_gap_section(self, skill_gaps: dict) -> list:
        """Build skill gap section."""
        elements = [
            Spacer(1, 0.5 * cm),
            Paragraph("🎯 Skill Gap Analysis", self.h2),
            HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY),
            Spacer(1, 0.3 * cm),
        ]

        missing = skill_gaps.get("missing_skills", []) if isinstance(skill_gaps, dict) else []
        present = skill_gaps.get("present_skills", []) if isinstance(skill_gaps, dict) else []
        recs = skill_gaps.get("recommendations", []) if isinstance(skill_gaps, dict) else []

        if present:
            elements.append(Paragraph("<b>✅ Matched Skills:</b>", self.body))
            skills_text = " | ".join(present[:15])
            elements.append(Paragraph(skills_text, self.body))
            elements.append(Spacer(1, 0.2 * cm))

        if missing:
            elements.append(Paragraph("<b>❌ Missing Skills:</b>", self.body))
            missing_text = " | ".join(missing[:15])
            elements.append(Paragraph(missing_text, self.body))
            elements.append(Spacer(1, 0.2 * cm))

        if recs:
            elements.append(Paragraph("<b>📚 Learning Recommendations:</b>", self.body))
            rec_data = [["Skill", "Priority", "Est. Time", "Resource"]]
            for r in recs[:6]:
                resources = r.get("resources", [{}])
                resource_name = resources[0].get("platform", "Online") if resources else "Online"
                rec_data.append([
                    r.get("skill", ""),
                    r.get("priority", "").upper(),
                    r.get("estimated_time", ""),
                    resource_name,
                ])

            rec_table = Table(rec_data, colWidths=[4 * cm, 2.5 * cm, 3 * cm, 4.5 * cm])
            rec_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, LIGHT]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(rec_table)

        return elements

    def _build_rewritten_bullets(self, bullets: list) -> list:
        """Build STAR rewritten bullets section."""
        elements = [
            Spacer(1, 0.5 * cm),
            Paragraph("✍️ STAR-Format Resume Improvements", self.h2),
            HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY),
            Spacer(1, 0.3 * cm),
        ]

        for i, bullet in enumerate(bullets[:5], 1):
            if isinstance(bullet, dict):
                original = bullet.get("original", "")
                rewritten = bullet.get("rewritten", "")
            else:
                original = str(bullet)
                rewritten = str(bullet)

            elements.append(Paragraph(f"<b>#{i} Original:</b>", self.body))
            elements.append(Paragraph(f"<i>{original}</i>", self.body))
            elements.append(Paragraph(f"<b>✨ Improved:</b>", self.body))

            improved_style = ParagraphStyle(
                "Improved",
                parent=self.body,
                leftIndent=10,
                textColor=SUCCESS,
                fontName="Helvetica-Bold",
            )
            elements.append(Paragraph(rewritten, improved_style))
            elements.append(Spacer(1, 0.3 * cm))

        return elements

    def _build_interview_questions(self, questions: list) -> list:
        """Build interview questions section."""
        elements = [
            Spacer(1, 0.5 * cm),
            Paragraph("🎤 Personalized Interview Questions", self.h2),
            HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY),
            Spacer(1, 0.3 * cm),
        ]

        if isinstance(questions, dict):
            # Structured format
            for category, qs in questions.items():
                if qs and isinstance(qs, list):
                    elements.append(Paragraph(f"<b>{category.replace('_', ' ').title()}:</b>", self.body))
                    for q in qs[:3]:
                        question_text = q.get("question", str(q)) if isinstance(q, dict) else str(q)
                        elements.append(Paragraph(f"• {question_text}", self.body))
                    elements.append(Spacer(1, 0.2 * cm))
        elif isinstance(questions, list):
            for i, q in enumerate(questions[:10], 1):
                q_text = q.get("question", str(q)) if isinstance(q, dict) else str(q)
                elements.append(Paragraph(f"<b>Q{i}.</b> {q_text}", self.body))

        return elements

    async def generate(
        self,
        resume_data: dict,
        ats_score: float,
        ats_breakdown: dict,
        skill_gaps: dict,
        rewritten_bullets: list,
        interview_questions: list,
        resume_id: str,
        job_id: str,
    ) -> str:
        """Generate the full PDF report and return the file path."""

        report_filename = f"report_{resume_id[:8]}_{job_id[:8]}.pdf"
        report_path = os.path.join(settings.REPORTS_DIR, report_filename)

        doc = SimpleDocTemplate(
            report_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title="AI Resume Analysis Report",
            author="AI Resume Intelligence Platform",
        )

        candidate_name = resume_data.get("name", "Candidate")
        job_title = ats_breakdown.get("job_title", "Target Role") if isinstance(ats_breakdown, dict) else "Target Role"

        story = []
        story += self._build_header(candidate_name, job_title)
        story += self._build_ats_score_section(ats_score, ats_breakdown)
        story += self._build_breakdown_table(ats_breakdown)
        story += self._build_skill_gap_section(skill_gaps)

        if rewritten_bullets:
            story += self._build_rewritten_bullets(rewritten_bullets)

        if interview_questions:
            story += self._build_interview_questions(interview_questions)

        # Footer
        story.append(Spacer(1, cm))
        story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
        footer_style = ParagraphStyle(
            "Footer",
            parent=self.styles["Normal"],
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
        )
        story.append(Paragraph(
            f"Generated by AI Resume Intelligence Platform | {datetime.now().strftime('%Y-%m-%d %H:%M')} | Confidential",
            footer_style,
        ))

        doc.build(story)
        logger.info(f"✅ PDF report generated: {report_path}")
        return report_path
