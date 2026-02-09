from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.controllers.agentController import ask_agent


class AgentRequest(BaseModel):
    """Schema for agent question request"""
    question: str


class AgentResponse(BaseModel):
    """Schema for agent response"""
    status: str
    answer: str
    tool_used: bool
    error: Optional[str] = None


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/ask", response_model=AgentResponse)
def agent_ask_endpoint(request: AgentRequest):
    """Ask the agent a question. Agent decides whether to check the knowledge base."""
    try:
        result = ask_agent(request.question)
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
