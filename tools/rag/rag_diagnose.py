"""
RAG Diagnostics Tool
Finds incomplete or missing RAG entries
"""

import logging
from typing import Dict, Any, List
from tools.plex.plex_utils import stream_all_media, stream_subtitles
from tools.rag.rag_storage import load_ingested_items, get_ingestion_stats

logger = logging.getLogger("mcp_server")


def diagnose_rag() -> Dict[str, Any]:
    """
    Diagnose RAG database for incomplete entries.

    Returns:
        Dictionary with diagnostic information
    """
    try:
        logger.info("🔍 Starting RAG diagnostics...")

        ingested_ids = load_ingested_items()
        missing_subtitles = []
        not_yet_ingested = []

        # Check all media items
        for media_item in stream_all_media():
            media_id = str(media_item["id"])
            title = media_item["title"]
            media_type = media_item["type"]

            # Check if already ingested
            if media_id not in ingested_ids:
                # Check if it has subtitles
                subtitle_lines = list(stream_subtitles(media_id))

                if not subtitle_lines:
                    missing_subtitles.append({
                        "title": title,
                        "id": media_id,
                        "type": media_type
                    })
                    logger.info(f"❌ No subtitles: {title}")
                else:
                    not_yet_ingested.append({
                        "title": title,
                        "id": media_id,
                        "type": media_type,
                        "subtitle_lines": len(subtitle_lines)
                    })
                    logger.info(f"⏳ Not yet ingested: {title} ({len(subtitle_lines)} subtitle lines)")

        stats = get_ingestion_stats()

        result = {
            "total_items": stats["total_items"],
            "ingested_count": stats["total_ingested"],
            "missing_subtitles": missing_subtitles,
            "not_yet_ingested": not_yet_ingested,
            "statistics": {
                "items_with_no_subtitles": len(missing_subtitles),
                "items_ready_to_ingest": len(not_yet_ingested),
                "completion_percentage": round((stats["total_ingested"] / stats["total_items"] * 100), 2) if stats[
                                                                                                                 "total_items"] > 0 else 0
            }
        }

        logger.info(f"📊 Diagnostics complete:")
        logger.info(f"  - Total items: {stats['total_items']}")
        logger.info(f"  - Ingested: {stats['total_ingested']}")
        logger.info(f"  - Missing subtitles: {len(missing_subtitles)}")
        logger.info(f"  - Ready to ingest: {len(not_yet_ingested)}")

        return result

    except Exception as e:
        logger.error(f"❌ Diagnostics error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}