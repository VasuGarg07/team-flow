from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserRead
from app.models import User
from sqlalchemy.orm import Session
from app.database import get_db
import app.services.user_service as user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserRead, status_code=201)
def create_user_endpoint(data: UserCreate, db: Session = Depends(get_db)) -> User:
    return user_service.create_user(db, data)

@router.get("/{user_id}", response_model=UserRead)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)) -> User:
    return user_service.get_user(db, user_id)
