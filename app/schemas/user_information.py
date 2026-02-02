from pydantic import BaseModel

class UserInformationCreate(BaseModel):
    """Schema for creating a new user information - client sends this"""
    user_id: int
    name: str
    lastName: str
    address: str


class UserInformationRead(BaseModel):
    """Schema for reading/returning an item - API sends this"""
    id: int
    user_id: int
    name: str
    lastName: str
    address: str

    class Config:
        from_attributes = True  # Allows Pydantic to read from SQLAlchemy models