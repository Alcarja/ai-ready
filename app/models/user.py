from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum
from app.database import Base


class UserRole(str, Enum):
    """Define allowed user roles"""
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(SQLEnum(UserRole), index=True, default=UserRole.user)

    # Relationship to UserInformation (one-to-many)
    user_information = relationship("UserInformation", back_populates="user")
