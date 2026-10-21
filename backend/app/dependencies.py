from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.errors import UnauthorizedError
from app.security import decode_access_token
from app.repositories.user_repository import get_user_by_id


bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing token")

    try:
        user_id = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid or expired token")

    user = get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("Invalid or expired token")

    return user