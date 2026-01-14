"""
Plex Ingestion Tool
Ingests Plex media subtitles into RAG database with parallelizable functions
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from tools.rag.rag_storage import check_if_ingested, mark_as_ingested, get_ingestion_stats

logger = logging.getLogger("mcp_server")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROGRESS_FILE = PROJECT_ROOT / "data" / "plex_ingest_progress.json"
PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Import Plex utilities
from .plex_utils import stream_all_media, extract_metadata, stream_subtitles, chunk_stream

# Import RAG add function
from tools.rag.rag_add import rag_add


def load_progress() -> Dict[str, bool]:
    """Load ingestion progress from disk"""
    if not PROGRESS_FILE.exists():
        return {}

    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_progress(progress: Dict[str, bool]) -> None:
    """Save ingestion progress to disk"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


# ============================================================================
# REFACTORED FUNCTIONS FOR MULTI-AGENT PARALLELIZATION
# ============================================================================

def find_unprocessed_items(limit: int, rescan_no_subtitles: bool = False) -> List[Dict[str, Any]]:
    """
    STEP 1: Find unprocessed media items (parallelizable - just discovery)

    Args:
        limit: Maximum number of unprocessed items to find
        rescan_no_subtitles: Whether to re-check items with no subtitles

    Returns:
        List of unprocessed media items with metadata
    """
    unprocessed_items = []
    checked_count = 0

    logger.info(f"🔍 Finding {limit} unprocessed items (rescan: {rescan_no_subtitles})")

    for media_item in stream_all_media():
        media_id = str(media_item["id"])
        title = media_item["title"]

        # Check if already ingested
        if check_if_ingested(media_id, skip_no_subtitles=rescan_no_subtitles):
            checked_count += 1
            logger.debug(f"⏭️  [{checked_count}] Already processed: {title}")
            continue

        # Found unprocessed item
        logger.info(f"📍 Found unprocessed: {title}")
        unprocessed_items.append(media_item)

        # Stop when we have enough
        if len(unprocessed_items) >= limit:
            break

    logger.info(f"🔍 Found {len(unprocessed_items)} unprocessed items (checked {checked_count + len(unprocessed_items)} total)")
    return unprocessed_items


def extract_subtitles_for_item(media_item: Dict[str, Any]) -> Tuple[str, str, List[str], str]:
    """
    STEP 2: Extract subtitles for a single item (parallelizable - independent per item)

    Args:
        media_item: Media item dictionary

    Returns:
        Tuple of (media_id, title, subtitle_lines, metadata_text)
    """
    media_id = str(media_item["id"])
    title = media_item["title"]

    logger.info(f"📥 Extracting subtitles for: {title}")

    # Get metadata
    metadata_text = extract_metadata(media_item)

    # Stream subtitles
    subtitle_lines = list(stream_subtitles(media_id))

    if not subtitle_lines:
        logger.warning(f"⚠️  No subtitles found for: {title}")
    else:
        logger.info(f"✅ Extracted {len(subtitle_lines)} subtitle lines for: {title}")

    return media_id, title, subtitle_lines, metadata_text


def ingest_item_to_rag(
    media_id: str,
    title: str,
    subtitle_lines: List[str],
    metadata_text: str
) -> Dict[str, Any]:
    """
    STEP 3: Ingest a single item's subtitles into RAG (parallelizable - independent per item)

    Args:
        media_id: Plex media ID
        title: Media title
        subtitle_lines: List of subtitle text lines
        metadata_text: Metadata description

    Returns:
        Dictionary with ingestion results
    """
    if not subtitle_lines:
        mark_as_ingested(media_id, status="no_subtitles")
        return {
            "title": title,
            "id": media_id,
            "subtitle_chunks": 0,
            "subtitle_word_count": 0,
            "status": "no_subtitles",
            "reason": "No subtitles found"
        }

    logger.info(f"💾 Ingesting {title} to RAG...")

    # Chunk and add to RAG
    chunks_added = 0
    word_count = 0

    for chunk in chunk_stream(iter(subtitle_lines), chunk_size=1600):
        result = rag_add(
            text=chunk,
            source=f"plex:{media_id}:{title}",
            chunk_size=400
        )
        if result.get("success"):
            chunks_added += result.get("chunks_added", 0)
            word_count += len(chunk.split())

    # Store metadata separately
    metadata_summary = f"{title} - {metadata_text}"
    if len(metadata_summary) < 1600:
        try:
            result = rag_add(
                text=metadata_summary,
                source=f"plex:{media_id}:metadata",
                chunk_size=400
            )
            if result.get("success"):
                chunks_added += result.get("chunks_added", 0)
        except Exception as e:
            logger.warning(f"⚠️  Could not add metadata chunk: {e}")

    mark_as_ingested(media_id, status="success")

    logger.info(f"✅ Ingested: {title} ({chunks_added} chunks, ~{word_count} words)")

    return {
        "title": title,
        "id": media_id,
        "subtitle_chunks": chunks_added,
        "subtitle_word_count": word_count,
        "status": "success"
    }


# ============================================================================
# MAIN ORCHESTRATION FUNCTION (Can use single or multi-agent)
# ============================================================================

def ingest_next_batch(limit: int = 5, rescan_no_subtitles: bool = False) -> Dict[str, Any]:
    """
    Ingest the next batch of unprocessed Plex items into RAG.

    This is the main orchestration function that can be used in:
    - Single-agent mode: Sequential processing
    - Multi-agent mode: Parallel processing (if multi-agent is available)

    Args:
        limit: Maximum number of NEW items to process
        rescan_no_subtitles: If True, re-check items that previously had no subtitles

    Returns:
        Dictionary with ingestion results including detailed item information
    """
    try:
        logger.info(f"📥 Starting batch ingestion (limit: {limit}, rescan: {rescan_no_subtitles})")

        # STEP 1: Find unprocessed items
        unprocessed_items = find_unprocessed_items(limit, rescan_no_subtitles)

        if not unprocessed_items:
            logger.info("✅ No unprocessed items found")
            stats = get_ingestion_stats()
            return {
                "ingested": [],
                "skipped": [],
                "stats": {
                    "total_items": stats["total_items"],
                    "successfully_ingested": stats["successfully_ingested"],
                    "missing_subtitles": stats["missing_subtitles"],
                    "remaining_unprocessed": stats["remaining"]
                },
                "items_processed": 0,
                "items_checked": 0
            }

        # STEP 2 & 3: Extract and ingest (sequential in single-agent mode)
        ingested_items = []
        skipped_items = []

        for media_item in unprocessed_items:
            # Extract subtitles
            media_id, title, subtitle_lines, metadata_text = extract_subtitles_for_item(media_item)

            # Ingest to RAG
            result = ingest_item_to_rag(media_id, title, subtitle_lines, metadata_text)

            if result["status"] == "success":
                ingested_items.append(result)
            else:
                skipped_items.append({
                    "title": result["title"],
                    "id": result["id"],
                    "reason": result.get("reason", "Unknown")
                })

        # Get total stats
        stats = get_ingestion_stats()

        result = {
            "ingested": ingested_items,
            "skipped": skipped_items,
            "stats": {
                "total_items": stats["total_items"],
                "successfully_ingested": stats["successfully_ingested"],
                "missing_subtitles": stats["missing_subtitles"],
                "remaining_unprocessed": stats["remaining"]
            },
            "items_processed": len(unprocessed_items),
            "items_checked": len(unprocessed_items)
        }

        logger.info(f"📊 Batch complete:")
        logger.info(f"   - Items processed: {len(unprocessed_items)}")
        logger.info(f"   - Ingested: {len(ingested_items)}")
        logger.info(f"   - Skipped: {len(skipped_items)}")

        return result

    except Exception as e:
        logger.error(f"❌ Ingestion error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# ============================================================================
# HELPER FOR MULTI-AGENT: Process multiple items in parallel
# ============================================================================

async def ingest_batch_parallel(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple items in parallel (for multi-agent use)

    Args:
        items: List of media items to process

    Returns:
        List of ingestion results
    """
    import asyncio

    async def process_item(media_item):
        """Async wrapper for processing a single item"""
        loop = asyncio.get_event_loop()

        # Extract subtitles
        media_id, title, subtitle_lines, metadata_text = await loop.run_in_executor(
            None, extract_subtitles_for_item, media_item
        )

        # Ingest to RAG
        result = await loop.run_in_executor(
            None, ingest_item_to_rag, media_id, title, subtitle_lines, metadata_text
        )

        return result

    # Process all items in parallel
    results = await asyncio.gather(*[process_item(item) for item in items])
    return results