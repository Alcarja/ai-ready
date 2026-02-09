from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.controllers.llmController import ask_llm


class AskRequest(BaseModel):
    """Schema for question vectorization request"""
    question: str


class SearchResult(BaseModel):
    """Schema for a single search result"""
    document: str
    similarity: float
    chunk_id: str
    metadata: dict


class AskResponse(BaseModel):
    """Schema for question vectorization and search response"""
    question: str
    embedding: Optional[list[float]] = None
    embedding_model: str
    status: str
    error: Optional[str] = None
    search_results: list[SearchResult] = []


router = APIRouter(prefix="/ask", tags=["llm"])


@router.post("/", response_model=AskResponse)
def ask_endpoint(request: AskRequest):
    """Vectorize a question and return its embedding"""
    try:
        result = ask_llm(request.question)
        return AskResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
