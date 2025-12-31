import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_add(title, content, tags):
    """
    Add a knowledge base entry.

    Stores creation timestamp in UTC, but includes local time for display.
    """
    entry_id = str(uuid.uuid4())
    created_at_utc = datetime.now(timezone.utc).isoformat()

    entry = {
        "id": entry_id,
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": created_at_utc
    }

    KB_DIR.mkdir(parents=True, exist_ok=True)
    file_path = KB_DIR / f"{entry_id}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2)

    # Add local time for client display
    created_at_local = datetime.fromisoformat(created_at_utc).astimezone().isoformat()
    entry["created_at_local"] = created_at_local

    return entry
