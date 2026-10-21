from sqlalchemy.orm import Session

from app.schemas.auth import LoginRequest, TokenResponse
from app.repositories.user_repository import get_user_by_email
from app.security import verify_password, create_access_token
from app.errors import UnauthorizedError

def login(db: Session, data: LoginRequest) -> TokenResponse:
    user = get_user_by_email(db, data.email.strip().lower())
    if user is None or not verify_password(data.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    token = create_access_token(user_id=user.id)
    return TokenResponse(access_token=token, token_type="bearer")