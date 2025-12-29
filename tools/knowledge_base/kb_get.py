import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_get(entry_id):
    file = KB_DIR / f"{entry_id}.json"
    if not file.exists():
        return {"error": "Entry not found"}

    with open(file) as f:
        return json.load(f)
