"""
RAG Vector Database
Handles storage and retrieval of embeddings
"""

import logging
import uuid
from typing import Dict, Any, List
from langchain_ollama import OllamaEmbeddings

from .rag_utils import load_rag_db, save_rag_db

logger = logging.getLogger("mcp_server")

# Initialize embeddings model
embeddings_model = OllamaEmbeddings(model="bge-large")


def add_to_rag(text: str, source: str = None) -> Dict[str, Any]:
    """
    Add a single text chunk to the RAG database.

    Args:
        text: Text chunk to add
        source: Source identifier (e.g., "plex:12345")

    Returns:
        Dictionary with success status
    """
    try:
        # Load existing database
        db = load_rag_db()

        # Generate embedding for the text
        logger.debug(f"🔮 Generating embedding for text (length: {len(text)})")
        embedding = embeddings_model.embed_query(text)

        # Create document entry
        doc_id = str(uuid.uuid4())
        doc = {
            "id": doc_id,
            "text": text,
            "embedding": embedding,
            "metadata": {
                "source": source,
                "length": len(text),
                "word_count": len(text.split())
            }
        }

        # Add to database
        db.append(doc)

        # Save database
        save_rag_db(db)

        logger.debug(f"✅ Added document {doc_id} to RAG")

        return {
            "success": True,
            "id": doc_id,
            "length": len(text)
        }

    except Exception as e:
        logger.error(f"❌ Error adding to RAG: {e}")
        raise  # Re-raise to be caught by rag_add


def get_rag_stats() -> Dict[str, Any]:
    """
    Get statistics about the RAG database.

    Returns:
        Dictionary with database statistics
    """
    try:
        db = load_rag_db()

        if not db:
            return {
                "total_documents": 0,
                "total_words": 0,
                "sources": []
            }

        total_words = sum(doc["metadata"]["word_count"] for doc in db)
        sources = list(set(doc["metadata"]["source"] for doc in db if doc["metadata"].get("source")))

        return {
            "total_documents": len(db),
            "total_words": total_words,
            "sources": sources,
            "unique_sources": len(sources)
        }

    except Exception as e:
        logger.error(f"❌ Error getting RAG stats: {e}")
        return {
            "error": str(e)
        }