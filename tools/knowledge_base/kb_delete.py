from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_delete(entry_id: str):
    file = KB_DIR / f"{entry_id}.json"
    if not file.exists():
        return {"error": "Entry not found", "id": entry_id}

    file.unlink()
    return {"status": "deleted", "id": entry_id}
