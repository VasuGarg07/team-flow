from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from .config import app_settings
from .errors import UnauthorizedError


password_hash = PasswordHash.recommended()
ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = app_settings.JWT_SECRET_KEY
ALGORITHM = app_settings.JWT_ALGORITHM

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_hash.verify(password, hash)

def create_token(subject: int, token_type: str, lifetime: timedelta) -> str:
    expires_at = datetime.now(timezone.utc) + lifetime
    payload = {"sub": str(subject), "type": token_type,"exp": expires_at}
    return jwt.encode(payload, app_settings.JWT_SECRET_KEY, algorithm=app_settings.JWT_ALGORITHM)

def read_token(token: str, expected_type: str) -> int:
    try:
        payload = jwt.decode(token, app_settings.JWT_SECRET_KEY, algorithms=[app_settings.JWT_ALGORITHM])
        if (payload.get("type") != expected_type):
            raise jwt.InvalidTokenError("wrong token type")
        return int(payload["sub"])
    
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid or expired token")

def create_access_token(user_id: int) -> str:
    return create_token(user_id, "access", timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES))

def decode_access_token(token: str) -> int:
    return read_token(token, "access")

def create_refresh_token(user_id: int) -> str:
    return create_token(user_id, "refresh", timedelta(days=app_settings.REFRESH_TOKEN_EXPIRE_DAYS))

def decode_refresh_token(token: str) -> int:
    return read_token(token, "refresh")