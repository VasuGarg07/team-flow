import app.services.user_service as user_service
from fastapi import APIRouter, Depends
from app.schemas.user import UserCreate, UserRead
from sqlalchemy.orm import Session
from app.models import User
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
def register_user_endpoint(data: UserCreate, db: Session = Depends(get_db)) -> User:
    return user_service.create_user(db, data)