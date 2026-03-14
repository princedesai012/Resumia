"""
RAG Embedder — Uses google.generativeai directly for embeddings.

WHY: langchain-google-genai 2.x (GoogleGenerativeAIEmbeddings) uses the new
google-genai SDK which returns 404 on v1beta. We call google.generativeai
directly — the original SDK that is confirmed to work.

This module provides a simple embed_texts() function that FAISS can call.
"""

import os
import logging

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def configure_genai():
    """Configure google.generativeai with the API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
    return api_key


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts into vectors using google.generativeai embed_content.
    Returns a list of embedding vectors (list of floats).
    """
    configure_genai()
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=texts,
        task_type="retrieval_document"
    )
    # embed_content returns {"embedding": [...]} for single or {"embedding": [[...],...]} for batch
    embeddings = result.get("embedding", [])
    # Normalize: if a list of floats (single), wrap in list
    if embeddings and isinstance(embeddings[0], float):
        return [embeddings]
    return embeddings


def embed_query(query: str) -> list[float]:
    """Embed a single query string for semantic search."""
    configure_genai()
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=query,
        task_type="retrieval_query"
    )
    return result.get("embedding", [])
