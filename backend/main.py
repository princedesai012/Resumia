import os
import io
import logging
import psutil
import platform
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from pdfminer.high_level import extract_text
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Windows-specific setup
if platform.system() == 'Windows':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

app = FastAPI(title="Resume Analyzer API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://172.20.204.83:3000"],
    allow_methods=["POST"],
    allow_headers=["*"],
    allow_credentials=True
)

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("Missing GEMINI_API_KEY in .env file")
    raise RuntimeError("API key not configured")

def configure_gemini():
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("Gemini AI configured successfully.")
    except Exception as e:
        logger.error(f"Failed to configure Gemini AI: {e}")

configure_gemini()

MODEL_NAME = "gemini-1.5-flash"

def retry_gemini_request(model, text, retries=3):
    for attempt in range(retries):
        try:
            return model.generate_content(
                f"""You are an expert Resume Analyzer AI. Your task is to meticulously analyze the provided resume text and return ONLY a valid JSON object, adhering strictly to the specified format and constraints. Do not include any introductory text, explanations, or markdown formatting around the JSON output.**Analysis Context & Criteria:: {{"score": 0-100, "summary": "5 bullet points max", "top_skills": ["skill1", "skill2", "skill3"], "improvements": ["actionable_item1", "actionable_item2", "actionable_item3", "actionable_item4", "actionable_item5"]}} Resume: {text[:45000]}""",
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2000
                }
            )
        except Exception as e:
            logger.error(f"AI Request Failed (Attempt {attempt + 1}): {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
    raise HTTPException(500, detail="AI Service unavailable after multiple attempts")

@app.post("/api/analyze")
async def analyze_resume(file: UploadFile = File(...)):
    try:
        logger.info(f"Received file: {file.filename}")

        if not file.filename.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
            raise HTTPException(400, detail="Invalid file type. Only PDF, DOC, DOCX, and TXT are allowed")

        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(400, detail="Empty file received")

        if len(contents) > 5 * 1024 * 1024:
            raise HTTPException(400, detail="File size exceeds 5MB limit")

        # Extract text from PDF or plain text
        text = extract_text(io.BytesIO(contents)) if file.filename.lower().endswith('.pdf') else contents.decode('utf-8')
        logger.info(f"Extracted {len(text)} characters from {file.filename}")

        # Analyze with Gemini
        model = genai.GenerativeModel(MODEL_NAME)
        response = retry_gemini_request(model, text)

        logger.info("Analysis completed successfully.")
        return {"data": response.text}

    except HTTPException as e:
        logger.error(f"HTTPException: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Internal server error")

@app.get("/health")
async def health_check():
    memory = psutil.virtual_memory()
    cpu_usage = psutil.cpu_percent()
    
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "api_ready": bool(GEMINI_API_KEY),
        "memory": {
            "total": f"{memory.total / 1e9:.2f} GB",
            "available": f"{memory.available / 1e9:.2f} GB",
            "usage_percent": memory.percent
        },
        "cpu_usage_percent": cpu_usage
    }
