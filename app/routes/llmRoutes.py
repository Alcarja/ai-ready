from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.controllers.llmController import ask_llm


class AskRequest(BaseModel):
    """Schema for LLM question request"""
    question: str
    system_prompt: str | None = None  # Optional custom system prompt


class AskResponse(BaseModel):
    """Schema for LLM response"""
    answer: str


router = APIRouter(prefix="/ask", tags=["llm"])


@router.post("/", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    """Ask the LLM a question and get an answer"""
    try:
        answer = ask_llm(request.question, request.system_prompt)
        return AskResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
