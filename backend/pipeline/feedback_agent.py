"""
Agent 3: Strategic Feedback Generator Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Synthesizes Agent 1 + Agent 2 + FAISS context using google.generativeai directly.

WHY: langchain-google-genai 2.x uses an incompatible v1beta API endpoint.
We call google.generativeai directly — confirmed to work in original main.py.
"""

import os
import json
import logging
import re
import asyncio
from typing import List, Dict, Any

import google.generativeai as genai

from prompts.feedback_prompt import FEEDBACK_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class FeedbackAgent:
    """
    Agent 3: Strategic Career Feedback Generator.
    Synthesizes all pipeline outputs into a personalized improvement plan.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 8192,
            }
        )
        logger.info("FeedbackAgent initialized (using google.generativeai directly).")

    def _build_prompt(
        self,
        parsed_resume: dict,
        ats_analysis: dict,
        jd_text: str,
        job_role: str
    ) -> str:
        # Unescape {{ }} from the system prompt (they were escaped for LangChain)
        system = FEEDBACK_SYSTEM_PROMPT.replace("{{", "{").replace("}}", "}")
        human = (
            f"Generate a strategic improvement plan based on the following analysis:\n\n"
            f"━━━ PARSED RESUME (Agent 1 Output) ━━━\n"
            f"{json.dumps(parsed_resume, indent=2, ensure_ascii=False)}\n\n"
            f"━━━ ATS COMPLIANCE ANALYSIS (Agent 2 Output) ━━━\n"
            f"{json.dumps(ats_analysis, indent=2, ensure_ascii=False)}\n\n"
            f"━━━ RELEVANT JOB DESCRIPTIONS (FAISS Retrieval) ━━━\n"
            f"{jd_text}\n\n"
            f"━━━ TARGET ROLE ━━━\n{job_role}\n\n"
            f"Return ONLY the JSON object with your strategic recommendation plan."
        )
        return f"{system}\n\n{human}"

    async def run(
        self,
        parsed_resume: Dict[str, Any],
        ats_analysis: Dict[str, Any],
        relevant_jds: List[str],
        job_role: str = "software engineer"
    ) -> Dict[str, Any]:
        logger.info(f"FeedbackAgent: Generating strategic feedback for role='{job_role}'...")

        jd_text = (
            "\n\n---\n\n".join(f"[JD Chunk {i+1}]\n{c}" for i, c in enumerate(relevant_jds))
            if relevant_jds else "No job description context available."
        )

        prompt = self._build_prompt(parsed_resume, ats_analysis, jd_text, job_role)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self.model.generate_content, prompt
            )
            raw = response.text.strip()
            raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)

            result = json.loads(raw)
            logger.info(
                f"FeedbackAgent: Generated {len(result.get('prioritized_improvements', []))} "
                f"improvements, {len(result.get('quick_wins', []))} quick wins."
            )
            return result

        except Exception as e:
            logger.error(f"FeedbackAgent failed: {e}", exc_info=True)
            return self._fallback_feedback()

    def _fallback_feedback(self) -> Dict[str, Any]:
        logger.warning("FeedbackAgent: Returning fallback feedback.")
        return {
            "overall_verdict": "Could not generate feedback at this time. Please retry.",
            "interview_probability": "Unknown",
            "skill_gap_analysis": {"critical_missing": [], "nice_to_have_missing": [], "strong_matches": []},
            "narrative_assessment": {"summary_strength": "Unknown", "summary_feedback": "", "career_coherence": ""},
            "prioritized_improvements": [],
            "quick_wins": [],
            "skill_development_roadmap": {"30_days": [], "60_days": [], "90_days": []},
            "rewrite_suggestions": [],
            "error": "FeedbackAgent encountered an error. Please retry."
        }
