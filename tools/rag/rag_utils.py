import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import uuid

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAG_DB_PATH = PROJECT_ROOT / "data" / "rag_documents.json"
RAG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_rag_db() -> List[Dict[str, Any]]:
    """Load the RAG database from disk"""
    if not RAG_DB_PATH.exists():
        return []

    try:
        with open(RAG_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_rag_db(documents: List[Dict[str, Any]]) -> None:
    """Save the RAG database to disk"""
    with open(RAG_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a_arr = np.array(a)
    b_arr = np.array(b)

    dot_product = np.dot(a_arr, b_arr)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)

    return chunks