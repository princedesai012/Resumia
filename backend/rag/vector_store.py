"""
RAG Vector Store — FAISS semantic retrieval using google.generativeai directly.

Architecture:
  - Builds FAISS index from job description .txt files at startup.
  - Uses google.generativeai embed_content for embeddings (NOT langchain-google-genai).
  - Singleton pattern: index built once, reused for all requests.
  - Provides query() and query_with_scores() for semantic JD retrieval.
"""

import os
import json
import logging
import numpy as np
from typing import List, Tuple, Optional

from rag.embedder import embed_texts, embed_query

logger = logging.getLogger(__name__)

FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index")
JD_DIR = os.path.join(os.path.dirname(__file__), "job_descriptions")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.error("FAISS not installed. Run: pip install faiss-cpu")


class RAGRetriever:
    """
    Singleton FAISS-based retriever for industry-specific job descriptions.
    Uses google.generativeai embeddings directly (no LangChain wrapper).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        logger.info("RAGRetriever: Initializing (first time setup)...")
        self.index = None          # FAISS index
        self.documents: List[str] = []    # Parallel list of text chunks
        self.metadata: List[dict] = []    # Parallel list of metadata

        try:
            self._load_or_build_index()
            logger.info(f"RAGRetriever: Ready. {len(self.documents)} chunks indexed.")
        except Exception as e:
            logger.error(f"RAGRetriever: Init failed: {e}", exc_info=True)
            logger.warning("RAGRetriever: Will operate without JD context.")

        self._initialized = True

    # ──────────────────────────────────────────────────────────
    # Index Build / Persist / Load
    # ──────────────────────────────────────────────────────────

    def _load_or_build_index(self):
        """Load saved index from disk, or build fresh from JD files."""
        index_file = os.path.join(FAISS_INDEX_PATH, "index.bin")
        meta_file  = os.path.join(FAISS_INDEX_PATH, "metadata.json")

        if os.path.exists(index_file) and os.path.exists(meta_file):
            logger.info(f"Loading existing FAISS index from {FAISS_INDEX_PATH}")
            try:
                self.index = faiss.read_index(index_file)
                with open(meta_file, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self.documents = saved["documents"]
                self.metadata  = saved["metadata"]
                logger.info(f"Loaded {len(self.documents)} chunks from disk.")
                return
            except Exception as e:
                logger.warning(f"Failed to load index: {e}. Rebuilding...")

        self._build_index_from_jd_files()
        self._save_index()

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Simple character-level chunker."""
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return [c.strip() for c in chunks if c.strip()]

    def _build_index_from_jd_files(self):
        """Reads JD .txt files, chunks them, embeds them, builds FAISS index."""
        if not os.path.exists(JD_DIR):
            raise FileNotFoundError(f"JD directory not found: {JD_DIR}")

        jd_files = [f for f in os.listdir(JD_DIR) if f.endswith(".txt")]
        if not jd_files:
            raise ValueError(f"No .txt JD files found in {JD_DIR}")

        logger.info(f"Building FAISS index from {len(jd_files)} JD file(s): {jd_files}")

        all_chunks: List[str] = []
        all_metadata: List[dict] = []

        for fname in jd_files:
            fpath = os.path.join(JD_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()

            role_name = fname.replace(".txt", "").replace("_", " ").title()
            chunks = self._chunk_text(content)

            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadata.append({"role": role_name, "source": fname, "chunk_index": i})

            logger.info(f"  '{role_name}': {len(chunks)} chunks.")

        logger.info(f"Embedding {len(all_chunks)} chunks via google.generativeai...")

        # Embed in batches of 20 (API limit)
        all_embeddings = []
        batch_size = 20
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i: i + batch_size]
            vecs = embed_texts(batch)
            all_embeddings.extend(vecs)

        # Build FAISS flat L2 index
        dim = len(all_embeddings[0])
        self.index = faiss.IndexFlatL2(dim)
        vectors = np.array(all_embeddings, dtype=np.float32)
        self.index.add(vectors)

        self.documents = all_chunks
        self.metadata  = all_metadata
        logger.info(f"FAISS index built: {self.index.ntotal} vectors, dim={dim}")

    def _save_index(self):
        """Persist FAISS index + metadata to disk."""
        try:
            os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
            faiss.write_index(self.index, os.path.join(FAISS_INDEX_PATH, "index.bin"))
            with open(os.path.join(FAISS_INDEX_PATH, "metadata.json"), "w", encoding="utf-8") as f:
                json.dump({"documents": self.documents, "metadata": self.metadata}, f)
            logger.info(f"FAISS index saved to {FAISS_INDEX_PATH}")
        except Exception as e:
            logger.warning(f"Could not save FAISS index: {e}")

    # ──────────────────────────────────────────────────────────
    # Query
    # ──────────────────────────────────────────────────────────

    def query(self, skills: List[str], job_role: str, k: int = 3) -> List[str]:
        """
        Retrieve k most relevant JD chunks for the candidate profile.
        Returns empty list if index unavailable.
        """
        if self.index is None or not self.documents:
            logger.warning("RAG: index not available. Returning empty context.")
            return []

        skills_str = ", ".join(skills[:20]) if skills else "general technical skills"
        query_text = f"Job description for {job_role}. Required skills: {skills_str}"

        try:
            q_vec = embed_query(query_text)
            q_arr = np.array([q_vec], dtype=np.float32)
            distances, indices = self.index.search(q_arr, k=min(k, len(self.documents)))
            results = [self.documents[i] for i in indices[0] if i >= 0]
            logger.info(f"RAG: retrieved {len(results)} chunks for role='{job_role}'.")
            return results
        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            return []

    def query_with_scores(self, skills: List[str], job_role: str, k: int = 3) -> List[Tuple[str, float]]:
        """Same as query() but also returns L2 distances."""
        if self.index is None or not self.documents:
            return []

        skills_str = ", ".join(skills[:20]) if skills else "general technical skills"
        query_text = f"Job description for {job_role}. Required skills: {skills_str}"
        q_vec = embed_query(query_text)
        q_arr = np.array([q_vec], dtype=np.float32)
        distances, indices = self.index.search(q_arr, k=min(k, len(self.documents)))
        return [(self.documents[i], float(distances[0][j])) for j, i in enumerate(indices[0]) if i >= 0]
