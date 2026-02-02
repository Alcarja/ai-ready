from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ItemCreate(BaseModel):
    """Schema for creating a new item - client sends this"""
    name: str
    description: Optional[str] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item - client sends this"""
    name: Optional[str] = None
    description: Optional[str] = None


class ItemRead(BaseModel):
    """Schema for reading/returning an item - API sends this"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True  # Allows Pydantic to read from SQLAlchemy models