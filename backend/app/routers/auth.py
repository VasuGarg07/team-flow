
from fastapi import APIRouter, Depends, Response
from fastapi.params import Cookie
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserRead
from app.models import User
from app.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import create_user
from app.services.auth_service import login, refresh
from app.dependencies import get_current_user
from app.config import app_settings

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_SECURE = app_settings.COOKIE_SECURE
MAX_AGE = app_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

@router.post("/register", response_model=UserRead, status_code=201)
def register_user_endpoint(data: UserCreate, db: Session = Depends(get_db)) -> User:
    return create_user(db, data)

@router.post("/login", response_model=TokenResponse, status_code=200)
def login_user_endpoint(data: LoginRequest, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    tokens = login(db, data)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        max_age=MAX_AGE,
        path="/auth"
    )
    return TokenResponse(access_token=tokens.access_token, token_type="bearer")

@router.get("/me", response_model=UserRead)
def me_endpoint(current_user: User = Depends(get_current_user)) -> User:
    return current_user

@router.post("/refresh", response_model=TokenResponse, status_code=200)
def refresh_endpoint(response: Response, refresh_token: str | None = Cookie(default=None), db: Session = Depends(get_db)) -> TokenResponse:
    tokens = refresh(db, refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
        max_age=MAX_AGE,
        path="/auth"
    )
    return TokenResponse(access_token=tokens.access_token, token_type="bearer")

@router.delete("/logout", status_code=204)
def logout_endpoint(response: Response) -> None:
    response.delete_cookie(key="refresh_token", path="/auth")