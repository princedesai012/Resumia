# Resumia: Autonomous Career Intelligence Agent

Resumia is an advanced, AI-powered career intelligence platform that helps candidates optimize their resumes and structure their career growth. It utilizes a powerful 3-agent orchestration pipeline backed by Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) to provide deep, actionable insights.

## 🚀 Features

Resumia employs a true **Agentic Pipeline** to process resumes. The backend orchestrates three distinct AI agents chronologically to deliver a comprehensive analysis:

1. **ParserAgent (Structural Parsing)**
   - Extracts structured resume data using LangChain's `FewShotPromptTemplate` for high-precision skill extraction.
   - Intelligently categorizes keywords, languages, and frameworks.

2. **RAG with FAISS Vector Store**
   - Semantically retrieves relevant industry Job Description (JD) chunks using the Gemini Text Embedding model (`embedding-001`) and a FAISS vector similarity search.
   - Provides deep context for the ATS scoring phase.

3. **ATSAgent (ATS Compliance Scoring)**
   - Scores the candidate's resume against an ATS rubric (5 dimensions) grounded by the retrieved JD context.
   - Pinpoints critical missing keywords, formatting issues, and structural gaps.

4. **FeedbackAgent (Strategic Career Generation)**
   - Synthesizes all outputs into a strategic career improvement plan.
   - Generates a prioritized action list and a structured 30/60/90 day roadmap to land the target role.

### 📝 Supported Formats & Roles
- **Formats:** PDF, DOCX, DOC, TXT.
- **Roles out-of-the-box:** `software_engineer`, `data_scientist`, `product_manager`.

---

## 🛠️ Technology Stack

### Backend
- **Python Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **AI Models:** Google Gemini API (`gemini-2.0-flash` for reasoning, `embedding-001` for RAG)
- **Agent Orchestration:** [LangChain](https://python.langchain.com/)
- **Vector Database:** [FAISS](https://faiss.ai/) (Facebook AI Similarity Search)
- **Document Processing:** `pdfminer.six` for PDFs, `python-docx` for Word documents

### Frontend
- **Framework:** React 18
- **Tooling:** Vite
- **Styling:** CSS / External Design Systems

---

## ⚙️ Installation & Setup

### Prerequisites
- Node.js (v18+)
- Python (3.9+)
- A [Google Gemini API Key](https://aistudio.google.com/)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/Resumia.git
cd Resumia
```

### 2. Backend Setup
Navigate to the `backend` directory and set up your Python environment.

```bash
cd backend
python -m venv venv

# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Start the FastAPI server:
```bash
uvicorn main:app --reload
# Server will run on http://localhost:8000
```

### 3. Frontend Setup
Open a new terminal and navigate to the `frontend` directory.

```bash
cd frontend
npm install
npm run dev
# Vite dev server will run on http://localhost:5173
```

---

## 📡 API Endpoints

Resumia exposes several RESTful endpoints from its FastAPI backend:

- `POST /api/analyze`: Main endpoint. Runs the full 3-agent career intelligence pipeline. Requires a file upload (`resume`) and an optional query parameter `job_role`.
- `POST /api/analyze/quick`: Fast mode. Only runs the ParserAgent for structural extraction (skipping RAG and Feedback generation).
- `GET /api/roles`: Returns the list of currently supported roles for JD matching.
- `GET /health`: Comprehensive system health check including memory usage, CPU usage, and FAISS initialization status.

---

## 🧠 Architecture Overview

Resumia is designed around an asynchronous pipeline model:

1. **Upload:** User provides a resume via the React interface.
2. **Extraction:** FastAPI extracts plaintext using format-specific miners (`pdfminer`, `python-docx`).
3. **Agent 1:** The `ParserAgent` converts unstructured text into a highly structured JSON profile.
4. **Knowledge Retrieval:** The RAG system embeds the extracted skills and queries the offline FAISS Vector Store to fetch relevant sub-chunks of Industry JDs.
5. **Agent 2:** The `ATSAgent` evaluates the structured parsed resume against the retrieved JD context to calculate an ATS compatibility score.
6. **Agent 3:** The `FeedbackAgent` takes the parsed profile, the JD context, and the ATS score to hallucination-free actionable advice.
7. **Delivery:** The structured response is sent back to the React UI, displaying the roadmap and parsing results to the user.

---

## 🤝 Contributing

Contributions are welcome! If you'd like to improve the ATS algorithm, add more supported job roles to the RAG vector store, or enhance the React UI:
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
