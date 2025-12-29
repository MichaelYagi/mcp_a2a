import json
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_add(title, content, tags):
    entry_id = str(uuid.uuid4())
    entry = {
        "id": entry_id,
        "title": title,
        "content": content,
        "tags": tags
    }

    KB_DIR.mkdir(parents=True, exist_ok=True)

    file_path = KB_DIR / f"{entry_id}.json"

    with open(file_path, "w") as f:
        json.dump(entry, f, indent=2)

    return entry