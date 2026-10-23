"""Tiny JSON-file store. Swap this module for Firebase later."""
import json
import os
import threading
from pathlib import Path

DATA_FILE = Path(os.getenv("LEARNMATE_DATA", Path(__file__).resolve().parent.parent / "data" / "students.json"))
LOCK = threading.RLock()


def load_all() -> dict:
    if not DATA_FILE.exists():
        return {}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_all(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, DATA_FILE)


def get_student(data: dict, name: str) -> dict:
    return data.setdefault(name, {"mastery": {}, "history": [], "sessions": {}})
