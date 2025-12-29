from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KB_DIR = SCRIPT_DIR / "entries"

def kb_delete_many(entry_ids):
    deleted = []
    missing = []

    for entry_id in entry_ids:
        file = KB_DIR / f"{entry_id}.json"
        if file.exists():
            file.unlink()
            deleted.append(entry_id)
        else:
            missing.append(entry_id)

    return {
        "deleted": deleted,
        "missing": missing
    }
