from pydantic import BaseModel

class UserCreate(BaseModel):
    """Schema for creating a new user - client sends this"""
    email: str
    password: str
    role: str


class UserRead(BaseModel):
    """Schema for reading/returning an item - API sends this"""
    id: int
    email: str
    password: str

    class Config:
        from_attributes = True  # Allows Pydantic to read from SQLAlchemy models