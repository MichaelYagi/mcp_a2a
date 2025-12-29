import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_search(query):
    results = []
    for file in KB_DIR.glob("*.json"):
        with open(file) as f:
            entry = json.load(f)
            if query.lower() in entry["title"].lower() or query.lower() in entry["content"].lower():
                results.append(entry)
    return results
