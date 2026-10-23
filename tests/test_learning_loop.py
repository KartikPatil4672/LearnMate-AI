import pytest
from fastapi.testclient import TestClient

from app import engine, storage
from app.main import app
from app.questions import BANK

P = {"first_name": "Ana", "last_name": "Lee", "course": "Python Programming"}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DATA_FILE", tmp_path / "students.json")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    return TestClient(app)


def answer_key(session_questions, wrong_topics=()):
    key = {q["id"]: next(b["answer"] for b in BANK if b["id"] == q["id"]) for q in session_questions}
    for q in session_questions:
        if q["topic"] in wrong_topics:
            key[q["id"]] = "Z"  # deliberately wrong
    return key


def test_scoring_and_weak_topics():
    qs = [b for b in BANK if b["level"] == "diag"]
    answers = {q["id"]: q["answer"] for q in qs}
    for q in qs:
        if q["topic"] == "Loops":
            answers[q["id"]] = "Z"
    res = engine.score_session(qs, answers)
    assert res["topics"]["Loops"] == 0
    assert res["topics"]["Functions"] == 100
    assert engine.weak_topics(engine.update_mastery({}, res["topics"])) == ["Loops"]


def test_mastery_blends_old_and_new():
    assert engine.update_mastery({"Loops": 0}, {"Loops": 100}) == {"Loops": 50}


def test_quiz_hides_answers(client):
    r = client.get("/api/quiz", params=P).json()
    assert r["questions"] and all("answer" not in q for q in r["questions"])


def test_full_learning_loop(client):
    quiz = client.get("/api/quiz", params=P).json()
    answers = answer_key(quiz["questions"], wrong_topics={"Loops"})
    res = client.post("/api/submit", json={**P, "session_id": quiz["session_id"], "answers": answers}).json()
    assert res["weak_topics"] == ["Loops"]
    assert res["study_plan"][0]["topic"] == "Loops"
    assert res["next_step"] == "practice"

    # Practice targets only the weak topic
    prac = client.get("/api/quiz", params={**P, "mode": "practice"}).json()
    assert {q["topic"] for q in prac["questions"]} == {"Loops"}
    answers = answer_key(prac["questions"])
    res2 = client.post("/api/submit", json={**P, "session_id": prac["session_id"], "answers": answers}).json()
    assert res2["mastery"]["Loops"] == 50  # blended 0 and 100
    assert res2["weak_topics"] == ["Loops"]

    hist = client.get("/api/progress", params=P).json()["history"]
    assert len(hist) == 2


def test_session_cannot_be_reused(client):
    quiz = client.get("/api/quiz", params=P).json()
    body = {**P, "session_id": quiz["session_id"], "answers": {}}
    assert client.post("/api/submit", json=body).status_code == 200
    assert client.post("/api/submit", json=body).status_code == 404


def test_practice_requires_diagnostic(client):
    assert client.get("/api/quiz", params={**P, "first_name": "New", "mode": "practice"}).status_code == 400


def test_bad_student_name(client):
    assert client.get("/api/quiz", params={**P, "first_name": "<b>"}).status_code == 400


def test_unknown_course(client):
    assert client.get("/api/quiz", params={**P, "course": "Underwater Basket Weaving"}).status_code == 400


def test_progress_is_separate_per_student(client):
    quiz = client.get("/api/quiz", params=P).json()
    client.post("/api/submit", json={**P, "session_id": quiz["session_id"], "answers": {}})
    other = client.get("/api/progress", params={**P, "last_name": "Kim"}).json()
    assert other["mastery"] == {} and other["attempts"] == 0
    assert client.get("/api/courses").json()["courses"] == ["Python Programming"]
