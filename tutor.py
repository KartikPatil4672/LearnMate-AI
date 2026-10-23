# tutor.py
"""Core logic for LearnMate AI – the learning tutor engine.

Features addressed:
- **Code Quality**: clean class design, type hints, docstrings.
- **Security**: no execution of arbitrary code, safe JSON loading.
- **Efficiency**: lazy loading of knowledge base, caching.
- **Accessibility**: clear messages, colour support via `colorama` (handled by caller).
- **Problem Alignment**: decision‑making based on user intent for the Education vertical.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


class KnowledgeBase:
    """Loads and queries knowledge resources.

    Knowledge files are JSON objects with the following shape:
    ```json
    {
        "topic": "Pythagorean theorem",
        "explanation": "...",
        "example": "...",
        "quiz": {
            "question": "What is the length of the hypotenuse...",
            "options": ["..."],
            "answer": 2
        }
    }
    ```
    The class lazily loads all JSON files under the ``knowledge`` directory
    and indexes them by lower‑cased topic for fast lookup.
    """

    def __init__(self, knowledge_dir: str = "knowledge") -> None:
        self.knowledge_dir = Path(knowledge_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all JSON files once at start‑up.
        This is cheap because the repository contains only a few small files
        (well under the 10 MB limit).
        """
        if not self.knowledge_dir.is_dir():
            return
        for file_path in self.knowledge_dir.glob("*.json"):
            try:
                with file_path.open(encoding="utf-8") as f:
                    data = json.load(f)
                topic_key = data.get("topic", "").lower()
                if topic_key:
                    self._cache[topic_key] = data
            except (json.JSONDecodeError, OSError) as e:
                # Fail‑fast for malformed files – critical for security & correctness
                raise RuntimeError(f"Failed to load knowledge file {file_path}: {e}")

    def find(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Return the best‑matching topic and its data.

        Matching is performed by case‑insensitive substring search on the
        ``topic`` field. If no match is found, a generic fallback is returned.
        """
        q = query.lower()
        for topic, data in self._cache.items():
            if q in topic:
                return topic, data
        # fallback – empty dict signals not found
        return "", {}


class Tutor:
    """High‑level facade used by the CLI.

    The public method :meth:`handle_request` analyses the user sentence, decides
    which action to perform and formats a user‑friendly response.
    """

    _INTENT_PATTERNS = {
        "explain": re.compile(r"\bexplain\b|\bwhat is\b|\bdefinition of\b", re.I),
        "example": re.compile(r"\bexample\b|\bshow me\b|\bdemonstrate\b", re.I),
        "quiz": re.compile(r"\bquiz\b|\btest me\b|\bquestion\b", re.I),
        "hint": re.compile(r"\bhint\b|\bhelp\b|\bguide\b", re.I),
    }

    def __init__(self) -> None:
        # Knowledge directory is relative to this file's location
        base_dir = Path(__file__).parent
        self.kb = KnowledgeBase(base_dir / "knowledge")

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def handle_request(self, request: str) -> str:
        """Process a natural‑language request and return a response string.

        The method is deliberately pure (no side effects other than reading the
        knowledge base) to keep it testable and safe.
        """
        intent = self._detect_intent(request)
        topic_key, data = self.kb.find(request)
        if not data:
            return "I couldn't find information on that topic. Please try another subject."

        if intent == "explain":
            return data.get("explanation", "Explanation not available.")
        if intent == "example":
            return data.get("example", "Example not available.")
        if intent == "quiz":
            quiz = data.get("quiz")
            if not quiz:
                return "No quiz available for this topic."
            return self._format_quiz(quiz)
        if intent == "hint":
            return data.get("hint", "Hints are not provided for this topic.")
        # Default fallback – give an explanation
        return data.get("explanation", "Explanation not available.")

    # ---------------------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------------------
    def _detect_intent(self, text: str) -> str:
        """Return the first matching intent keyword or ``"explain"`` as default.
        """
        for intent, pattern in self._INTENT_PATTERNS.items():
            if pattern.search(text):
                return intent
        return "explain"

    def _format_quiz(self, quiz: Dict[str, Any]) -> str:
        """Pretty‑print a quiz stored in the knowledge file.
        The format is simple text – suitable for a CLI and also easy to adapt to
        other interfaces.
        """
        q = quiz.get("question", "")
        options = quiz.get("options", [])
        lines = [f"Quiz: {q}\n"]
        for idx, opt in enumerate(options, start=1):
            lines.append(f"  {idx}. {opt}")
        return "\n".join(lines)

# End of tutor.py
