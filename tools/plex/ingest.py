"""
Plex Ingestion Tool
Ingests Plex media subtitles into RAG database
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
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


def ingest_next_batch(limit: int = 5, rescan_no_subtitles: bool = False) -> Dict[str, Any]:
    """
    Ingest the next batch of unprocessed Plex items into RAG.

    Args:
        limit: Maximum number of NEW items to process (not just check)
        rescan_no_subtitles: If True, re-check items that previously had no subtitles

    Returns:
        Dictionary with ingestion results including detailed item information
    """
    try:
        ingested_items = []
        skipped_items = []
        processed_count = 0  # Count of NEW items processed
        checked_count = 0  # Total items examined

        logger.info(f"📥 Starting batch ingestion (limit: {limit}, rescan: {rescan_no_subtitles})")

        # Stream through all media
        for media_item in stream_all_media():
            media_id = str(media_item["id"])
            title = media_item["title"]

            # Check if already ingested
            if check_if_ingested(media_id, skip_no_subtitles=rescan_no_subtitles):
                checked_count += 1
                logger.debug(f"⏭️  [{checked_count}] Already processed: {title}")
                # Don't count as processed - we want NEW items only
                continue

            # This is a NEW item to process
            logger.info(f"📥 [{checked_count + 1}] Processing: {title}")

            # Get metadata
            metadata_text = extract_metadata(media_item)

            # Stream subtitles
            subtitle_lines = list(stream_subtitles(media_id))

            if not subtitle_lines:
                logger.warning(f"⚠️  No subtitles found for: {title}")
                skipped_items.append({
                    "title": title,
                    "id": media_id,
                    "reason": "No subtitles found"
                })
                mark_as_ingested(media_id, status="no_subtitles")
                processed_count += 1

                # Check if we hit limit
                if processed_count >= limit:
                    logger.info(f"✅ Reached limit of {limit} new items processed")
                    break
                continue

            # Chunk and add to RAG
            chunks_added = 0
            word_count = 0

            for chunk in chunk_stream(iter(subtitle_lines), chunk_size=1600):
                # Just the subtitle text - DON'T save yet
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

            ingested_items.append({
                "title": title,
                "id": media_id,
                "subtitle_chunks": chunks_added,
                "subtitle_word_count": word_count
            })

            logger.info(f"✅ Ingested: {title} ({chunks_added} chunks, ~{word_count} words)")
            processed_count += 1

            # Check if we hit limit
            if processed_count >= limit:
                logger.info(f"✅ Reached limit of {limit} new items processed")
                break

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
            "items_processed": processed_count,
            "items_checked": checked_count + processed_count  # Total examined
        }

        logger.info(f"📊 Batch complete:")
        logger.info(f"   - Checked: {checked_count + processed_count} items")
        logger.info(f"   - New items processed: {processed_count}")
        logger.info(f"   - Ingested: {len(ingested_items)}")
        logger.info(f"   - Skipped: {len(skipped_items)}")

        return result

    except Exception as e:
        logger.error(f"❌ Ingestion error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}