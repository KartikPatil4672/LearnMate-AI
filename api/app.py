# api/app.py
"""FastAPI entry point for Vercel deployment of LearnMate AI.

POST /api/ask
{
    "question": "Explain the Pythagorean theorem"
}
→ {"response": "..."}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tutor import Tutor

app = FastAPI(title="LearnMate AI Tutor")
_tutor = Tutor()

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    response: str

@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    answer = _tutor.handle_request(request.question)
    return AskResponse(response=answer)

@app.get("/", include_in_schema=False)
def root():
    return {"message": "LearnMate AI is running – use POST /api/ask"}
