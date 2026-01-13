"""
RAG Utilities
Helper functions for RAG database management
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

logger = logging.getLogger("mcp_server")

# Database file location
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAG_DB_FILE = PROJECT_ROOT / "data" / "rag_database.json"


def ensure_data_dir():
    """Ensure the data directory exists"""
    RAG_DB_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_rag_db() -> List[Dict[str, Any]]:
    """
    Load the RAG database from disk.

    Returns:
        List of document dictionaries with embeddings
    """
    ensure_data_dir()

    if not RAG_DB_FILE.exists():
        logger.info("📂 RAG database file not found, starting fresh")
        return []

    try:
        with open(RAG_DB_FILE, 'r', encoding='utf-8') as f:
            db = json.load(f)

        logger.debug(f"📂 Loaded RAG database with {len(db)} documents")
        return db

    except Exception as e:
        logger.error(f"❌ Error loading RAG database: {e}")
        return []


def save_rag_db(db: List[Dict[str, Any]]):
    """
    Save the RAG database to disk.

    Args:
        db: List of document dictionaries with embeddings
    """
    ensure_data_dir()

    try:
        with open(RAG_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2)

        logger.debug(f"💾 Saved RAG database with {len(db)} documents")

    except Exception as e:
        logger.error(f"❌ Error saving RAG database: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Similarity score between 0 and 1
    """
    try:
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)

        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Clip to [0, 1] range
        return float(max(0.0, min(1.0, similarity)))

    except Exception as e:
        logger.error(f"❌ Error calculating cosine similarity: {e}")
        return 0.0


def clear_rag_db():
    """Clear the entire RAG database"""
    ensure_data_dir()

    if RAG_DB_FILE.exists():
        RAG_DB_FILE.unlink()
        logger.info("🗑️  Cleared RAG database")
    else:
        logger.info("📂 RAG database already empty")