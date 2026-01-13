"""
RAG Add Tool
Adds text to the RAG vector database with embedding generation
"""

import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger("mcp_server")


def split_text_by_words(text: str, max_words: int = 400) -> List[str]:
    """
    Split text into chunks by word count.

    Args:
        text: Text to split
        max_words: Maximum words per chunk (default: 400, safe for 512 token limit)

    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = ' '.join(words[i:i + max_words])
        chunks.append(chunk)

    return chunks


def rag_add(text: str, source: str = None, chunk_size: int = 400) -> Dict[str, Any]:
    """
    Add text to RAG database.

    Args:
        text: Text to add
        source: Source identifier (e.g., "plex:12345")
        chunk_size: Maximum words per chunk (reduced from 500 to 400 for safety)

    Returns:
        Dictionary with success status and metadata
    """
    from tools.rag.rag_vector_db import add_to_rag

    logger.info(f"📝 Adding text to RAG (length: {len(text)}, chunk_size: {chunk_size})")

    try:
        # Split into chunks (use smaller chunk size to avoid token limit)
        chunks = split_text_by_words(text, max_words=chunk_size)
        logger.info(f"📦 Split into {len(chunks)} chunks")

        # Add each chunk to RAG
        added_count = 0
        for i, chunk in enumerate(chunks):
            # Verify chunk isn't too long (safety check)
            if len(chunk) > 2000:  # ~500 tokens max
                logger.warning(f"⚠️  Chunk {i + 1} too long ({len(chunk)} chars), splitting further...")
                sub_chunks = split_text_by_words(chunk, max_words=300)
                for sub_chunk in sub_chunks:
                    add_to_rag(sub_chunk, source=source)
                    added_count += 1
            else:
                add_to_rag(chunk, source=source)
                added_count += 1

        logger.info(f"✅ Added {added_count} chunks to RAG")

        return {
            "success": True,
            "chunks_added": added_count,
            "source": source,
            "original_length": len(text)
        }

    except Exception as e:
        logger.error(f"❌ Error adding to RAG: {e}")
        return {
            "success": False,
            "error": str(e)
        }