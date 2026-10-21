from fastapi import APIRouter, Depends
from app.schemas.user import UserRead
from app.models import User
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
import app.services.user_service as user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{user_id}", response_model=UserRead)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
    return user_service.get_user(db, user_id)
