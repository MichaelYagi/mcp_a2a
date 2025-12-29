import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_list():
    entries = []
    for file in KB_DIR.glob("*.json"):
        with open(file) as f:
            entries.append(json.load(f))
    return entries
