from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user in the database"""
    db_item = User(email=user.email, password=user.password, role="user")
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item



