# tests/test_tutor.py
import unittest
from pathlib import Path
import sys

# Ensure the project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from tutor import Tutor, KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):
    def setUp(self):
        # Use the bundled knowledge directory
        self.kb = KnowledgeBase(str(PROJECT_ROOT / "learnmate-ai" / "knowledge"))

    def test_find_existing(self):
        topic, data = self.kb.find("pythagorean")
        self.assertTrue(topic)
        self.assertIn("explanation", data)
        self.assertIn("quiz", data)

    def test_find_missing(self):
        topic, data = self.kb.find("unknown topic")
        self.assertEqual(topic, "")
        self.assertEqual(data, {})

class TestTutor(unittest.TestCase):
    def setUp(self):
        self.tutor = Tutor()

    def test_explain_intent(self):
        resp = self.tutor.handle_request("Explain the Pythagorean theorem")
        self.assertIn("right‑angled triangle", resp)

    def test_quiz_intent(self):
        resp = self.tutor.handle_request("Quiz me on Pythagorean theorem")
        self.assertIn("Quiz:", resp)
        self.assertIn("What is the length of the hypotenuse", resp)

    def test_fallback(self):
        resp = self.tutor.handle_request("bla bla unknown")
        self.assertIn("couldn't find information", resp)

if __name__ == "__main__":
    unittest.main()
