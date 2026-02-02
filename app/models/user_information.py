from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class UserInformation(Base):
    __tablename__ = "user_information"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name= Column(String, index=True)
    lastName= Column(String, index=True)
    address= Column(String, index=True)

    # Relationship back to User
    user = relationship("User", back_populates="user_information")
