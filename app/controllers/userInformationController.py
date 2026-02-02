from sqlalchemy.orm import Session
from app.schemas.user_information import UserInformationCreate
from app.models.user_information import UserInformation
from app.models.user import User


def create_user_information(db: Session, userInformation: UserInformationCreate) -> UserInformation:
    """Create a new user information in the database"""
    # Check if the user exists before creating user information
    user = db.query(User).filter(User.id == userInformation.user_id).first()
    if not user:
        raise ValueError(f"User with ID {userInformation.user_id} does not exist")

    # Check if user information already exists for this user
    existing_info = db.query(UserInformation).filter(UserInformation.user_id == userInformation.user_id).first()
    if existing_info:
        raise ValueError(f"User information already exists for user ID {userInformation.user_id}")

    db_item = UserInformation(
        user_id=userInformation.user_id,
        name=userInformation.name,
        lastName=userInformation.lastName,
        address=userInformation.address
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item



