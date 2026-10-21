from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from .config import app_settings


password_hash = PasswordHash.recommended()
ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = app_settings.JWT_SECRET_KEY
ALGORITHM = app_settings.JWT_ALGORITHM

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_hash.verify(password, hash)

def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expires_at}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> int:
    payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload["sub"])