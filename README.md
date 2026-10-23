# LearnMate AI – Learning Tutor Assistant

## Overview
LearnMate AI is a **smart, dynamic learning tutor** that helps students across a variety of subjects. It adapts to the user’s context, offers explanations, quizzes, and step‑by‑step problem solving, and maintains a lightweight, maintainable codebase.

## Chosen Vertical
**Education – Learning Tutor**

## Approach & Logic
1. **Context‑aware interactions** – The assistant receives the learner’s current topic, difficulty level, and learning goals. It uses these to tailor explanations.
2. **Modular design** – Core logic lives in `tutor.py`. A thin CLI wrapper (`main.py`) handles I/O, making the engine reusable in other front‑ends (web, Slack, etc.).
3. **Decision‑making** – A simple rule‑based engine decides which action to take (explain, quiz, provide example, or give hints) based on user intent detected via prompt keywords.
4. **Extensible content** – Knowledge content is stored in JSON files (`knowledge/*.json`) that can be expanded without changing code.
5. **Testing** – Unit tests cover the decision engine and knowledge lookup to guarantee correctness.

## How It Works
1. Run `python main.py`.
2. Type a request like:
   - `Explain the Pythagorean theorem`
   - `Give me a beginner level quiz on photosynthesis`
   - `Show an example of solving a quadratic equation`
3. The assistant parses the request, selects the appropriate action, fetches content from the knowledge base, and prints a response.

## Assumptions
- The assistant runs locally; no external APIs are required.
- Knowledge is limited to the JSON files in the repo (easy to extend).
- Interaction is via a terminal/CLI for simplicity, but the core `Tutor` class can be imported elsewhere.

## Repository Rules (for the challenge)
- **Public** on GitHub.
- **Single branch** (`main`).
- **Size < 10 MB** (all content is lightweight text and JSON).

## Setup
```bash
# Clone the repo (replace <your‑username>)
git clone https://github.com/<your‑username>/learnmate-ai.git
cd learnmate-ai
# (Optional) create a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
# Run the tutor
python main.py
```

## License
MIT – feel free to fork and improve!
