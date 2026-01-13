"""
RAG Add Tool
Adds text to the RAG vector database with embedding generation
"""

import logging
from typing import Dict, Any, List
import json

logger = logging.getLogger("mcp_server")


def split_text_by_chars(text: str, max_chars: int = 1500) -> List[str]:
    """
    Split text into chunks by character count (safer than word count).

    Args:
        text: Text to split
        max_chars: Maximum characters per chunk (default: 1500, ~375 tokens)

    Returns:
        List of text chunks
    """
    chunks = []

    # Split by sentences first to avoid breaking mid-sentence
    sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')

    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence_length = len(sentence)

        # If adding this sentence would exceed limit and we have content, yield chunk
        if current_length + sentence_length > max_chars and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(sentence)
        current_length += sentence_length + 1  # +1 for space

    # Add remaining chunk
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks


def rag_add(text: str, source: str = None, chunk_size: int = 1500) -> Dict[str, Any]:
    """
    Add text to RAG database.

    Args:
        text: Text to add
        source: Source identifier (e.g., "plex:12345")
        chunk_size: Maximum characters per chunk (default: 1500)

    Returns:
        Dictionary with success status and metadata
    """
    from tools.rag.rag_vector_db import add_to_rag

    logger.info(f"📝 Adding text to RAG (length: {len(text)}, chunk_size: {chunk_size})")

    try:
        # Split into chunks by character count
        chunks = split_text_by_chars(text, max_chars=chunk_size)
        logger.info(f"📦 Split into {len(chunks)} chunks")

        # Add each chunk to RAG
        added_count = 0
        failed_count = 0

        for i, chunk in enumerate(chunks):
            chunk_length = len(chunk)
            logger.debug(f"  Chunk {i+1}: {chunk_length} chars")

            # Safety check - if chunk is still too long, split it further
            if chunk_length > chunk_size:
                logger.warning(f"⚠️  Chunk {i+1} still too long ({chunk_length} chars), splitting to max 1000 chars...")
                # Force split at 1000 chars
                sub_chunks = [chunk[j:j+1000] for j in range(0, len(chunk), 1000)]
                for sub_chunk in sub_chunks:
                    try:
                        add_to_rag(sub_chunk, source=source)
                        added_count += 1
                    except Exception as e:
                        logger.error(f"❌ Failed to add sub-chunk: {e}")
                        failed_count += 1
            else:
                try:
                    add_to_rag(chunk, source=source)
                    added_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to add chunk {i+1}: {e}")
                    failed_count += 1

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