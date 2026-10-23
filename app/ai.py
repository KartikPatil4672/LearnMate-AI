"""Gemini helpers. Every function returns None on any failure so callers can fall back."""
import json
import os
import uuid

import httpx

from .questions import TOPIC_NOTES


def enabled() -> bool:
    return bool(os.getenv("GEMINI_API_KEY", "").strip())


def _call(prompt: str):
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    resp = httpx.post(
        url,
        headers={"x-goog-api-key": os.getenv("GEMINI_API_KEY", "").strip()},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
        },
        timeout=25,
    )
    resp.raise_for_status()
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(text)


def generate_questions(topic: str, n: int = 3):
    """Targeted multiple-choice questions for a weak topic, or None."""
    if not enabled():
        return None
    prompt = (
        f"Write {n} beginner-level multiple-choice Python questions about '{topic}'. "
        'Return ONLY a JSON array. Each item: {"question": str, "options": {"A": str, "B": str, '
        '"C": str, "D": str}, "answer": "A"|"B"|"C"|"D"}. Exactly one option must be correct.'
    )
    try:
        items = _call(prompt)
        out = []
        for it in items[:n]:
            opts = it["options"]
            if set(opts) != set("ABCD") or it["answer"] not in opts or not str(it["question"]).strip():
                continue
            out.append({
                "id": f"ai-{uuid.uuid4().hex[:8]}",
                "topic": topic,
                "level": "practice",
                "question": str(it["question"]),
                "options": {k: str(v) for k, v in opts.items()},
                "answer": it["answer"],
                "source": "gemini",
            })
        return out or None
    except Exception:
        return None


def get_notes(topic: str) -> list:
    """3 short revision bullets: Gemini if available, otherwise the built-in notes."""
    fallback = TOPIC_NOTES.get(topic, [f"Review the basics of {topic}."])
    if not enabled():
        return fallback
    prompt = (
        f"Give 3 short revision bullet points for a beginner struggling with Python '{topic}'. "
        "Return ONLY a JSON array of 3 strings."
    )
    try:
        items = _call(prompt)
        notes = [str(x) for x in items if str(x).strip()][:3]
        return notes or fallback
    except Exception:
        return fallback
