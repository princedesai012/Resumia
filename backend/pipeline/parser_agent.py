"""
Agent 1: Structural Parser Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Uses google.generativeai directly (same as original working main.py) + 
manually-built few-shot prompt for high-precision resume parsing.

WHY: langchain-google-genai 2.x switched to the new google-genai SDK which
uses an incompatible v1beta endpoint. We bypass it entirely and call
google.generativeai directly — the SDK that is confirmed to work.
"""

import os
import json
import logging
import re
import asyncio

import google.generativeai as genai

from prompts.parser_prompt import PARSER_EXAMPLES, PARSER_PREFIX

logger = logging.getLogger(__name__)


class ParserAgent:
    """
    Agent 1: Structural Parser — extracts structured JSON from raw resume text.
    Uses few-shot prompting via google.generativeai (no LangChain LLM wrapper).
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 8192,
            }
        )
        logger.info("ParserAgent initialized (using google.generativeai directly).")

    def _build_prompt(self, resume_text: str) -> str:
        """Build the few-shot prompt as a plain Python string (no LangChain formatting)."""
        parts = [PARSER_PREFIX, "\n\n"]

        for i, ex in enumerate(PARSER_EXAMPLES, 1):
            parts.append(
                f"━━━ EXAMPLE {i} ━━━\n"
                f"RESUME:\n{ex['resume_snippet']}\n\n"
                f"PARSED JSON:\n{ex['output']}\n\n"
            )

        parts.append(
            f"Now parse the following resume. Return ONLY valid JSON.\n\n"
            f"━━━ TARGET RESUME ━━━\n{resume_text[:40000]}\n\n"
            f"━━━ PARSED JSON ━━━"
        )
        return "".join(parts)

    async def run(self, resume_text: str) -> dict:
        """Parse raw resume text into structured JSON."""
        logger.info(f"ParserAgent: Parsing resume ({len(resume_text)} chars)...")
        prompt = self._build_prompt(resume_text)

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self.model.generate_content, prompt
            )
            raw = response.text.strip()

            # Strip markdown code fences if present
            raw = re.sub(r'^```(?:json)?\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$', '', raw, flags=re.MULTILINE)

            result = json.loads(raw)
            logger.info(
                f"ParserAgent: Extracted {len(result.get('keywords', []))} keywords, "
                f"{len(result.get('experience', []))} experience entries."
            )
            return result

        except Exception as e:
            logger.error(f"ParserAgent failed: {e}", exc_info=True)
            return self._fallback_parse(resume_text)

    def _fallback_parse(self, resume_text: str) -> dict:
        logger.warning("ParserAgent: Using fallback parser.")
        return {
            "name": "Unknown",
            "contact": {},
            "summary": "",
            "skills": {"languages": [], "frameworks": [], "databases": [], "cloud_devops": [], "soft_skills": []},
            "experience": [],
            "education": [],
            "certifications": [],
            "total_experience_years": 0,
            "keywords": [],
            "raw_text_preview": resume_text[:500]
        }
