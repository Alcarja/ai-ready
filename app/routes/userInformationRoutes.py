from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user_information import UserInformationCreate, UserInformationRead
from app.controllers.userInformationController import (
    create_user_information as create_user_information_db,
)

router = APIRouter(prefix="/userInformation", tags=["userInformation"])

@router.post("/", response_model=UserInformationRead)
def create_user_information(userInformation: UserInformationCreate, db: Session = Depends(get_db)):
    """Create a new user information"""
    try:
        return create_user_information_db(db=db, userInformation=userInformation)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


