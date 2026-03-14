"""
Resumia: Autonomous Career Intelligence Agent
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FastAPI Orchestrator — coordinates the 3-agent agentic pipeline:

  Agent 1 (ParserAgent)   → Structural parsing with few-shot LangChain template
  Agent 2 (ATSAgent)      → ATS compliance scoring vs FAISS-retrieved JDs
  Agent 3 (FeedbackAgent) → Strategic career improvement plan generation

Technologies: Python, FastAPI, Google Gemini API, LangChain, FAISS (Vector DB)
"""

import os
import io
import logging
import platform
import time
from contextlib import asynccontextmanager

import psutil
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ── Pipeline Agents ────────────────────────────────────────────────────────────
from pipeline.parser_agent import ParserAgent
from pipeline.ats_agent import ATSAgent
from pipeline.feedback_agent import FeedbackAgent

# ── RAG Retriever ──────────────────────────────────────────────────────────────
from rag.vector_store import RAGRetriever

# ── Environment & Logging ──────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Windows async fix
if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ── Validate API Key ───────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in .env file")
    raise RuntimeError("API key not configured.")

# ── Supported Job Roles ────────────────────────────────────────────────────────
SUPPORTED_ROLES = [
    "software_engineer",
    "data_scientist",
    "product_manager"
]

# ── Application Lifespan (Startup/Shutdown) ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize ALL agents and FAISS index ONCE at startup.
    Storing on app.state avoids re-creating GenerativeModel objects per request.
    """
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)   # Configure once globally

    logger.info("=" * 60)
    logger.info("RESUMIA: Starting Autonomous Career Intelligence Agent")
    logger.info("=" * 60)

    # ── Initialize Agents (once) ───────────────────────────────
    logger.info("Initializing agents...")
    app.state.parser   = ParserAgent()
    app.state.ats      = ATSAgent()
    app.state.feedback = FeedbackAgent()
    logger.info("✓ ParserAgent | ATSAgent | FeedbackAgent ready.")

    # ── Initialize FAISS RAG (once) ────────────────────────────
    logger.info("Initializing FAISS RAG Retriever...")
    try:
        app.state.rag = RAGRetriever()
        chunks = len(app.state.rag.documents)
        logger.info(f"✓ FAISS ready with {chunks} JD chunks.")
    except Exception as e:
        logger.error(f"FAISS initialization failed: {e}")
        app.state.rag = None
        logger.warning("Server will run without RAG context.")

    logger.info("=" * 60)
    logger.info("All systems ready. Accepting requests.")
    logger.info("=" * 60)
    yield
    logger.info("RESUMIA: Shutting down...")


# ── FastAPI App ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Resumia: Autonomous Career Intelligence Agent",
    description=(
        "Agentic resume analysis pipeline: "
        "Structural Parsing → ATS Compliance Scoring → Strategic Feedback Generation. "
        "Powered by LangChain, Gemini, and FAISS Vector DB."
    ),
    version="2.0.0",
    lifespan=lifespan
)

# ── CORS ───────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://172.20.204.83:3000"
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    allow_credentials=True
)


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def extract_resume_text(file_content: bytes, filename: str) -> str:
    """Extract plain text from PDF, DOCX, or plain text file."""
    fname = filename.lower()

    if fname.endswith(".pdf"):
        return extract_text(io.BytesIO(file_content))

    elif fname.endswith(".docx"):
        if not DOCX_AVAILABLE:
            raise HTTPException(422, detail="python-docx not installed. Run: pip install python-docx")
        doc = DocxDocument(io.BytesIO(file_content))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)

    elif fname.endswith(".doc"):
        # .doc (legacy Word) — fall back to text decode with warning
        logger.warning(".doc format detected; conversion may be imperfect. Prefer PDF or DOCX.")
        return file_content.decode("utf-8", errors="ignore")

    else:
        # Plain .txt
        return file_content.decode("utf-8", errors="replace")


def validate_file(file: UploadFile, contents: bytes):
    """Validate file type and size."""
    allowed_extensions = (".pdf", ".txt", ".doc", ".docx")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    if len(contents) == 0:
        raise HTTPException(400, detail="Empty file received.")
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, detail="File size exceeds 5MB limit.")


# ══════════════════════════════════════════════════════════════════════════════
# PRIMARY ENDPOINT: Full Agentic Pipeline
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/analyze", summary="Run full 3-agent career intelligence pipeline")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)"),
    job_role: str = Query(
        default="software_engineer",
        description=f"Target job role. Supported: {', '.join(SUPPORTED_ROLES)}"
    )
):
    """
    Full Agentic Pipeline:

    1. **Agent 1 (ParserAgent)**: Extracts structured resume data using 
       FewShotPromptTemplate for high-precision skill extraction.

    2. **FAISS RAG**: Semantically retrieves relevant industry JD chunks 
       using Gemini text-embedding-004 + FAISS vector similarity search.

    3. **Agent 2 (ATSAgent)**: Scores resume against ATS rubric (5 dimensions)
       grounded by retrieved JD context.

    4. **Agent 3 (FeedbackAgent)**: Synthesizes all outputs into a strategic
       career improvement plan with prioritized actions and 30/60/90 day roadmap.
    """
    pipeline_start = time.time()
    logger.info(f"━━━ NEW REQUEST ━━━ file='{file.filename}', role='{job_role}'")

    # ── File Validation ──────────────────────────────────────────────────────
    contents = await file.read()
    validate_file(file, contents)

    # ── Text Extraction ──────────────────────────────────────────────────────
    try:
        resume_text = extract_resume_text(contents, file.filename)
        logger.info(f"Extracted {len(resume_text)} characters from '{file.filename}'.")
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(422, detail="Could not extract text from the file.")

    if len(resume_text.strip()) < 100:
        raise HTTPException(422, detail="Extracted text is too short. Please upload a valid resume.")

    # ── Normalize Job Role ───────────────────────────────────────────────────
    role_normalized = job_role.lower().replace(" ", "_")
    role_display = role_normalized.replace("_", " ").title()

    # ── AGENT 1: Structural Parsing ──────────────────────────────────────────
    logger.info("► Agent 1: Structural Parsing...")
    t1 = time.time()
    parsed_resume = await request.app.state.parser.run(resume_text)
    logger.info(f"  ✓ Parser done in {time.time()-t1:.2f}s")

    # ── RAG: FAISS Semantic Retrieval ────────────────────────────────────────
    logger.info("► FAISS RAG: Retrieving relevant JD chunks...")
    t2 = time.time()
    relevant_jds = []
    if request.app.state.rag is not None:
        try:
            all_skills = (
                parsed_resume.get("keywords", []) +
                parsed_resume.get("skills", {}).get("languages", []) +
                parsed_resume.get("skills", {}).get("frameworks", [])
            )
            relevant_jds = request.app.state.rag.query(
                skills=all_skills[:20], job_role=role_display, k=3
            )
        except Exception as e:
            logger.warning(f"  ⚠ RAG query failed: {e}")
    logger.info(f"  ✓ RAG retrieved {len(relevant_jds)} JD chunks in {time.time()-t2:.2f}s")

    # ── AGENT 2: ATS Compliance Scoring ─────────────────────────────────────
    logger.info("► Agent 2: ATS Compliance Scoring...")
    t3 = time.time()
    ats_result = await request.app.state.ats.run(parsed_resume, relevant_jds, role_display)
    logger.info(f"  ✓ ATS Score={ats_result.get('total_ats_score', 'N/A')} in {time.time()-t3:.2f}s")

    # ── AGENT 3: Strategic Feedback Generation ───────────────────────────────
    logger.info("► Agent 3: Strategic Feedback Generation...")
    t4 = time.time()
    feedback = await request.app.state.feedback.run(
        parsed_resume, ats_result, relevant_jds, role_display
    )
    logger.info(f"  ✓ Feedback generated in {time.time()-t4:.2f}s")

    # ── Pipeline Complete ────────────────────────────────────────────────────
    total_time = round(time.time() - pipeline_start, 2)
    logger.info(f"━━━ PIPELINE COMPLETE in {total_time}s ━━━")

    return {
        "status": "success",
        "pipeline_duration_seconds": total_time,
        "target_role": role_display,
        "agents": {
            "agent_1_parsed_resume": parsed_resume,
            "agent_2_ats_compliance": ats_result,
            "agent_3_strategic_feedback": feedback
        },
        "rag_metadata": {
            "jd_chunks_retrieved": len(relevant_jds),
            "embedding_model": "embedding-001",
            "vector_db": "FAISS"
        }
    }


# ══════════════════════════════════════════════════════════════════════════════
# SECONDARY ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/analyze/quick", summary="Quick analysis (Agent 1 only — fast parsing)")
async def quick_analyze(file: UploadFile = File(...)):
    """Run only Agent 1 (ParserAgent) for fast structural extraction without ATS scoring."""
    contents = await file.read()
    validate_file(file, contents)
    resume_text = extract_resume_text(contents, file.filename)

    parser = ParserAgent()
    parsed = await parser.run(resume_text)
    return {"status": "success", "parsed_resume": parsed}


@app.get("/api/roles", summary="List supported job roles")
async def get_supported_roles():
    """Returns the list of job roles supported for JD matching."""
    return {
        "supported_roles": SUPPORTED_ROLES,
        "note": "Pass one of these as ?job_role=<role> to /api/analyze"
    }


@app.get("/health", summary="System health check")
async def health_check():
    """Comprehensive health check: system resources + pipeline component status."""
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent()

    # Check FAISS index status
    rag_status = "unknown"
    try:
        rag = RAGRetriever()
        rag_status = "ready" if rag._initialized else "not_initialized"
    except Exception as e:
        rag_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "version": "2.0.0",
        "pipeline": {
            "agent_1": "ParserAgent (FewShotPromptTemplate)",
            "agent_2": "ATSAgent (ATS Rubric Scoring)",
            "agent_3": "FeedbackAgent (Strategic Career Coach)",
            "rag": f"FAISS Vector Store — {rag_status}"
        },
        "llm": "gemini-2.0-flash",
        "embedding_model": "embedding-001",
        "api_ready": bool(GEMINI_API_KEY),
        "supported_roles": SUPPORTED_ROLES,
        "system": {
            "memory_total_gb": f"{memory.total / 1e9:.2f}",
            "memory_available_gb": f"{memory.available / 1e9:.2f}",
            "memory_usage_percent": memory.percent,
            "cpu_usage_percent": cpu
        }
    }
