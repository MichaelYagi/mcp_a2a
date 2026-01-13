"""
RAG Add Tool
Adds text to the RAG vector database with embedding generation
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger("mcp_server")


def estimate_tokens(text: str) -> int:
    """
    Estimate token count (rough approximation).
    Rule of thumb: 1 token ≈ 4 characters for English text
    """
    return len(text) // 4


def split_text_safe(text: str, max_tokens: int = 400) -> List[str]:
    """
    Split text into token-safe chunks.

    Args:
        text: Text to split
        max_tokens: Maximum tokens per chunk (default: 400, safe for 512 limit)

    Returns:
        List of text chunks
    """
    # Convert tokens to characters (4 chars ≈ 1 token)
    max_chars = max_tokens * 4  # 400 tokens = 1600 chars

    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Get chunk
        end = min(start + max_chars, len(text))

        # If not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings in the last 20% of chunk
            search_start = start + int(max_chars * 0.8)
            for punct in ['. ', '! ', '? ', '\n\n']:
                last_punct = text.rfind(punct, search_start, end)
                if last_punct > start:
                    end = last_punct + len(punct)
                    break

        chunk = text[start:end].strip()
        if chunk:
            # Double-check token count
            estimated_tokens = estimate_tokens(chunk)
            if estimated_tokens > max_tokens:
                logger.warning(f"⚠️  Chunk has ~{estimated_tokens} tokens, splitting smaller...")
                # Force split at even smaller size
                smaller_max = max_tokens * 3  # 1200 chars for safety
                sub_end = start + smaller_max
                chunk = text[start:sub_end].strip()

            chunks.append(chunk)
            start = end
        else:
            start = end

    return chunks

def split_text_by_chars(text: str, max_chars: int = 2800, overlap: int = 200) -> List[str]:
    """
    Split text into chunks by character count (safer than word count).

    Args:
        text: Text to split
        max_chars: Maximum characters per chunk (default: 4000, ~375 tokens)

    Returns:
        List of text chunks
        :param text:
        :param max_chars:
        :param overlap:
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Get chunk
        end = start + max_chars

        # If not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings near the end
            for punct in ['. ', '! ', '? ', '\n']:
                last_punct = text.rfind(punct, start, end)
                if last_punct > start + (max_chars * 0.8):  # At least 80% of max size
                    end = last_punct + 1
                    break

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start with overlap (for context continuity)
        start = end - overlap if end < len(text) else len(text)

    return chunks


def rag_add(text: str, source: str = None, chunk_size: int = 400) -> Dict[str, Any]:
    """
    Add text to RAG database with token-safe chunking.

    Args:
        text: Text to add
        source: Source identifier (e.g., "plex:12345")
        chunk_size: Maximum TOKENS per chunk (default: 400 tokens = ~1600 chars)

    Returns:
        Dictionary with success status and metadata
    """
    from tools.rag.rag_vector_db import add_to_rag_batch, flush_batch

    logger.info(f"📝 Adding text to RAG (length: {len(text)}, max_tokens: {chunk_size}) for {source}")

    try:
        # Split into token-safe chunks
        chunks = split_text_safe(text, max_tokens=chunk_size)
        logger.info(f"📦 Split into {len(chunks)} chunks")

        # Add each chunk
        added_count = 0
        failed_count = 0

        for i, chunk in enumerate(chunks):
            chunk_length = len(chunk)
            estimated_tokens = estimate_tokens(chunk)
            logger.debug(f"  Chunk {i + 1}: {chunk_length} chars (~{estimated_tokens} tokens)")

            try:
                add_to_rag_batch(chunk, source=source)
                added_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to add chunk {i + 1} ({estimated_tokens} tokens): {e}")
                failed_count += 1

        # Flush batch after all chunks
        flush_batch()

        if failed_count > 0:
            logger.warning(f"⚠️  Added {added_count} chunks, {failed_count} failed")
        else:
            logger.info(f"✅ Added {added_count} chunks to RAG")

        return {
            "success": added_count > 0,
            "chunks_added": added_count,
            "chunks_failed": failed_count,
            "source": source,
            "original_length": len(text)
        }

    except Exception as e:
        logger.error(f"❌ Error adding to RAG: {e}")
        return {
            "success": False,
            "error": str(e)
        }