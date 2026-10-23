"""The learning loop: score -> mastery -> weak topics -> study plan."""
from collections import defaultdict

WEAK_THRESHOLD = 60  # percent
OLD_WEIGHT = 0.5     # how much past mastery counts when a new result arrives


def score_session(questions: list, answers: dict) -> dict:
    total = defaultdict(int)
    right = defaultdict(int)
    review = []
    score = 0
    for q in questions:
        given = answers.get(q["id"])
        ok = given == q["answer"]
        total[q["topic"]] += 1
        if ok:
            score += 1
            right[q["topic"]] += 1
        review.append({
            "id": q["id"],
            "topic": q["topic"],
            "question": q["question"],
            "your_answer": given,
            "correct_answer": q["answer"],
            "correct": ok,
        })
    topics = {t: round(right[t] / total[t] * 100) for t in total}
    n = len(questions)
    return {
        "score": score,
        "total": n,
        "percentage": round(score / n * 100) if n else 0,
        "topics": topics,
        "review": review,
    }


def update_mastery(old: dict, session_topics: dict) -> dict:
    new = dict(old)
    for topic, pct in session_topics.items():
        if topic in new:
            new[topic] = round(new[topic] * OLD_WEIGHT + pct * (1 - OLD_WEIGHT))
        else:
            new[topic] = pct
    return new


def weak_topics(mastery: dict) -> list:
    weak = [t for t, m in mastery.items() if m < WEAK_THRESHOLD]
    return sorted(weak, key=lambda t: mastery[t])  # weakest first


def build_plan(mastery: dict, notes_fn) -> list:
    weak = weak_topics(mastery)
    if not weak:
        return [{
            "topic": "All topics",
            "mastery": round(sum(mastery.values()) / len(mastery)) if mastery else 0,
            "action": "Great work! No weak topics. Retake the diagnostic later to keep skills fresh.",
            "notes": [],
        }]
    return [{
        "topic": t,
        "mastery": mastery[t],
        "action": f"Read the notes below, then take a targeted practice round on {t}.",
        "notes": notes_fn(t),
    } for t in weak]
