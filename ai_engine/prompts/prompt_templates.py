"""
All LLM prompt templates for the AI agents
Optimized for Mistral-7B-Instruct token efficiency
"""

# ── Resume Parsing Prompt ─────────────────────────────────────────────────────
RESUME_PARSE_PROMPT = """<s>[INST] Extract structured information from this resume text. 
Return ONLY valid JSON with these exact keys:
{{
  "summary": "professional summary",
  "education": [{{"institution": "", "degree": "", "field": "", "year": ""}}],
  "experience": [{{"company": "", "role": "", "duration": "", "bullets": []}}],
  "projects": [{{"name": "", "description": "", "technologies": []}}],
  "skills": ["skill1", "skill2"],
  "certifications": [{{"name": "", "issuer": "", "year": ""}}]
}}

Resume text:
{resume_text}

Return ONLY the JSON object, no explanation. [/INST]"""


# ── JD Parsing Prompt ─────────────────────────────────────────────────────────
JD_PARSE_PROMPT = """<s>[INST] Extract key information from this job description.
Return ONLY valid JSON:
{{
  "job_title": "",
  "company": "",
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "responsibilities": ["resp1"],
  "qualifications": ["qual1"],
  "experience_required": "",
  "education_required": ""
}}

Job Description:
{jd_text}

Return ONLY the JSON object. [/INST]"""


# ── Skill Gap Analysis Prompt ─────────────────────────────────────────────────
SKILL_GAP_PROMPT = """<s>[INST] Compare the candidate's skills with the job requirements.
Identify gaps and provide learning recommendations.
Return ONLY valid JSON:
{{
  "present_skills": ["skills candidate has that match"],
  "missing_skills": ["required skills candidate lacks"],
  "partial_skills": ["skills candidate partially has"],
  "recommendations": [
    {{"skill": "skill name", "resource": "course/book name", "platform": "Coursera/Udemy/YouTube", "priority": "high/medium/low"}}
  ],
  "overall_fit": "strong/moderate/weak"
}}

Candidate Skills: {candidate_skills}
Required Skills: {required_skills}

Return ONLY JSON. [/INST]"""


# ── ATS Analysis Prompt ───────────────────────────────────────────────────────
ATS_ANALYSIS_PROMPT = """<s>[INST] Analyze keyword match between resume and job description.
Return ONLY valid JSON:
{{
  "matched_keywords": ["keyword1"],
  "missing_keywords": ["keyword2"],
  "keyword_density": 0.75,
  "format_issues": ["issue1"],
  "strengths": ["strength1"],
  "improvements": ["improvement1"]
}}

Resume Text (excerpt): {resume_text}
Job Description (excerpt): {jd_text}

Return ONLY JSON. [/INST]"""


# ── STAR Rewrite Prompt ───────────────────────────────────────────────────────
STAR_REWRITE_PROMPT = """<s>[INST] Rewrite these resume bullet points using the STAR methodology 
(Situation, Task, Action, Result) to make them more impactful and ATS-friendly.
Also align them with the target job description.

Target Role: {job_title}

Original Bullets:
{original_bullets}

Return ONLY valid JSON:
{{
  "rewritten_bullets": [
    {{"original": "...", "rewritten": "...", "star_type": "action/result focused"}}
  ],
  "tips": ["tip1", "tip2"]
}}

Return ONLY JSON. [/INST]"""


# ── Interview Question Generation Prompt ──────────────────────────────────────
INTERVIEW_QUESTIONS_PROMPT = """<s>[INST] Generate personalized interview questions based on the candidate's 
resume and the job description. Include behavioral, technical, and situational questions.

Job Title: {job_title}
Candidate Skills: {candidate_skills}
Candidate Experience: {experience_summary}

Return ONLY valid JSON:
{{
  "technical": [
    {{"question": "...", "difficulty": "easy/medium/hard", "hint": "what to look for"}}
  ],
  "behavioral": [
    {{"question": "...", "star_guidance": "how to structure answer"}}
  ],
  "situational": [
    {{"question": "...", "ideal_response_elements": ["element1"]}}
  ],
  "culture_fit": [
    {{"question": "..."}}
  ]
}}

Return ONLY JSON. [/INST]"""


# ── Career Recommendation Prompt ──────────────────────────────────────────────
CAREER_RECOMMENDATION_PROMPT = """<s>[INST] Based on the candidate's profile and skill gaps, 
provide actionable career development recommendations.

Candidate Profile: {profile_summary}
Missing Skills: {missing_skills}
Target Role: {target_role}

Return ONLY valid JSON:
{{
  "immediate_actions": ["action1"],
  "short_term_goals": ["goal1"],
  "long_term_goals": ["goal2"],
  "certifications_recommended": [
    {{"name": "", "provider": "", "relevance": "high/medium"}}
  ],
  "salary_range": "$X - $Y (estimated)",
  "career_path": ["current role → next role → target role"]
}}

Return ONLY JSON. [/INST]"""
