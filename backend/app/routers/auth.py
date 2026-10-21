
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserRead
from app.models import User
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import create_user
from app.services.auth_service import login
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead, status_code=201)
def register_user_endpoint(data: UserCreate, db: Session = Depends(get_db)) -> User:
    return create_user(db, data)

@router.post("/login", response_model=TokenResponse, status_code=200)
def login_user_endpoint(data: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return login(db, data)

@router.get("/me", response_model=UserRead)
def me_endpoint(current_user: User = Depends(get_current_user)) -> User:
    return current_user