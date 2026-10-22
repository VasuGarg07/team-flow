from sqlalchemy.orm import Session

from app.schemas.auth import LoginRequest, AuthTokens
from app.repositories.user_repository import get_user_by_email, get_user_by_id
from app.security import verify_password, create_access_token, create_refresh_token, decode_refresh_token
from app.errors import UnauthorizedError

def login(db: Session, data: LoginRequest) -> AuthTokens:
    user = get_user_by_email(db, data.email.strip().lower())
    if user is None or not verify_password(data.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    return AuthTokens(
        access_token=create_access_token(user_id=user.id), 
        refresh_token=create_refresh_token(user_id=user.id)
    )

def refresh(db: Session, token: str | None) -> AuthTokens:
    if token is None:
        raise UnauthorizedError("Missing refresh token")

    user_id = decode_refresh_token(token)
    user = get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("Invalid token")

    return AuthTokens(
        access_token=create_access_token(user_id=user.id), 
        refresh_token=create_refresh_token(user_id=user.id)
    )