"""
Agent 2: ATS Compliance Scorer Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scores parsed resume against FAISS-retrieved JDs using google.generativeai directly.

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

from prompts.ats_prompt import ATS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# ATS dimension weights for score calculation
ATS_WEIGHTS = {
    "keyword_match": 0.35,
    "action_verbs": 0.20,
    "quantified_achievements": 0.25,
    "section_completeness": 0.10,
    "format_compliance": 0.10,
}


class ATSAgent:
    """
    Agent 2: ATS Compliance Scorer.
    5 dimensions, weighted rubric, grounded by real FAISS JD chunks.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 8192,
            }
        )
        logger.info("ATSAgent initialized (using google.generativeai directly).")

    def _build_prompt(self, parsed_resume: dict, jd_text: str, job_role: str) -> str:
        # Use the system prompt (which has {{ }} already escaped — undo for direct use)
        system = ATS_SYSTEM_PROMPT.replace("{{", "{").replace("}}", "}")
        human = (
            f"Please score the following resume:\n\n"
            f"━━━ PARSED RESUME ━━━\n"
            f"{json.dumps(parsed_resume, indent=2, ensure_ascii=False)}\n\n"
            f"━━━ RELEVANT JOB DESCRIPTIONS ━━━\n"
            f"{jd_text}\n\n"
            f"━━━ TARGET JOB ROLE ━━━\n{job_role}\n\n"
            f"Apply the 5-dimension ATS rubric and return ONLY a valid JSON object."
        )
        return f"{system}\n\n{human}"

    async def run(
        self,
        parsed_resume: Dict[str, Any],
        relevant_jds: List[str],
        job_role: str = "software engineer"
    ) -> Dict[str, Any]:
        logger.info(f"ATSAgent: Scoring for role='{job_role}', JD chunks={len(relevant_jds)}...")

        jd_text = (
            "\n\n---\n\n".join(f"[JD Chunk {i+1}]\n{c}" for i, c in enumerate(relevant_jds))
            if relevant_jds else "No job description data available."
        )

        prompt = self._build_prompt(parsed_resume, jd_text, job_role)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self.model.generate_content, prompt
            )
            raw = response.text.strip()
            raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)

            result = json.loads(raw)
            result = self._ensure_total_score(result)

            logger.info(
                f"ATSAgent: Score={result.get('total_ats_score')}, "
                f"Grade={result.get('ats_grade')}, Pass={result.get('pass_threshold')}"
            )
            return result

        except Exception as e:
            logger.error(f"ATSAgent failed: {e}", exc_info=True)
            return self._fallback_score()

    def _ensure_total_score(self, result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if "dimensions" in result and "total_ats_score" not in result:
                dims = result["dimensions"]
                total = sum(
                    dims.get(k, {}).get("score", 0) * w
                    for k, w in ATS_WEIGHTS.items()
                )
                result["total_ats_score"] = round(total, 1)

            if "total_ats_score" in result and "ats_grade" not in result:
                s = result["total_ats_score"]
                result["ats_grade"] = (
                    "A" if s >= 90 else "B" if s >= 80 else
                    "C" if s >= 70 else "D" if s >= 60 else "F"
                )
                result["pass_threshold"] = s >= 70
        except Exception as e:
            logger.warning(f"Score recalc error: {e}")
        return result

    def _fallback_score(self) -> Dict[str, Any]:
        logger.warning("ATSAgent: Returning fallback score.")
        return {
            "total_ats_score": 0, "ats_grade": "F", "pass_threshold": False,
            "error": "ATS scoring failed. Please retry.", "dimensions": {}
        }
