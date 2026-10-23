"""LearnMate AI - FastAPI app. Run with:  python run.py"""
import random
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, Query  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from . import ai, engine, storage  # noqa: E402
from .questions import BANK, COURSES, public_view  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
MAX_SESSIONS = 5
NAME_RE = r"[\w .'\-]{1,40}"

app = FastAPI(title="LearnMate AI", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SubmitRequest(BaseModel):
    first_name: str
    last_name: str
    course: str
    session_id: str
    answers: dict[str, str]


def clean_name(value: str, label: str) -> str:
    value = " ".join(value.split())
    if not re.fullmatch(NAME_RE, value):
        raise HTTPException(400, f"{label} must be 1-40 letters, digits, spaces, dots, apostrophes or dashes.")
    return value


def identify(first_name: str, last_name: str, course: str):
    """Return (storage key, profile). Progress is kept separately per student and course."""
    first = clean_name(first_name, "First name")
    last = clean_name(last_name, "Surname")
    if course not in COURSES:
        raise HTTPException(400, "Unknown course.")
    key = f"{first.lower()} {last.lower()} | {course}"
    return key, {"first_name": first, "last_name": last, "course": course}


def bank_fallback(course: str, topic: str, n: int = 3) -> list:
    items = [dict(q) for q in BANK if q["course"] == course and q["topic"] == topic]
    return random.sample(items, k=min(n, len(items)))


@app.get("/api/health")
def health():
    return {"status": "ok", "gemini": ai.enabled()}


@app.get("/api/courses")
def courses():
    return {"courses": COURSES}


@app.get("/api/quiz")
def get_quiz(first_name: str = Query(...), last_name: str = Query(...),
             course: str = Query(...), mode: str = Query("diagnostic")):
    key, profile = identify(first_name, last_name, course)
    with storage.LOCK:
        data = storage.load_all()
        st = storage.get_student(data, key)
        st["profile"] = profile

        if mode == "diagnostic":
            questions = [dict(q) for q in BANK if q["level"] == "diag" and q["course"] == course]
        elif mode == "practice":
            if not st["mastery"]:
                raise HTTPException(400, "Take the diagnostic quiz first.")
            targets = engine.weak_topics(st["mastery"]) or [min(st["mastery"], key=st["mastery"].get)]
            questions = []
            for topic in targets[:3]:
                questions += ai.generate_questions(topic, 3) or bank_fallback(course, topic)
        else:
            raise HTTPException(400, "mode must be 'diagnostic' or 'practice'.")

        sid = uuid.uuid4().hex
        st["sessions"][sid] = {"mode": mode, "questions": questions}
        while len(st["sessions"]) > MAX_SESSIONS:
            st["sessions"].pop(next(iter(st["sessions"])))
        storage.save_all(data)

    return {"session_id": sid, "mode": mode, "questions": [public_view(q) for q in questions]}


@app.post("/api/submit")
def submit(req: SubmitRequest):
    key, profile = identify(req.first_name, req.last_name, req.course)
    with storage.LOCK:
        data = storage.load_all()
        st = storage.get_student(data, key)
        st["profile"] = profile
        session = st["sessions"].pop(req.session_id, None)
        if session is None:
            raise HTTPException(404, "Quiz session not found or already submitted.")

        result = engine.score_session(session["questions"], req.answers)
        st["mastery"] = engine.update_mastery(st["mastery"], result["topics"])
        weak = engine.weak_topics(st["mastery"])
        plan = engine.build_plan(st["mastery"], ai.get_notes)
        st["history"].append({
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "mode": session["mode"],
            "score": result["score"],
            "total": result["total"],
            "percentage": result["percentage"],
            "topics": result["topics"],
        })
        storage.save_all(data)

    return {
        **result,
        "mastery": st["mastery"],
        "weak_topics": weak,
        "study_plan": plan,
        "next_step": "practice" if weak else "done",
    }


@app.get("/api/progress")
def progress(first_name: str = Query(...), last_name: str = Query(...), course: str = Query(...)):
    key, profile = identify(first_name, last_name, course)
    with storage.LOCK:
        st = storage.get_student(storage.load_all(), key)
    return {
        "profile": profile,
        "mastery": st["mastery"],
        "weak_topics": engine.weak_topics(st["mastery"]),
        "attempts": len(st["history"]),
        "history": st["history"][-20:],
    }


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
