import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_search_tags(tag):
    results = []
    for file in KB_DIR.glob("*.json"):
        with open(file) as f:
            entry = json.load(f)
            if tag in entry.get("tags", []):
                results.append(entry)
    return results
