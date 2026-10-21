from sqlalchemy.orm import Session
from app.schemas.user import UserCreate
from app.models import User
import app.repositories.user_repository as UserRepo

def create_user(db: Session, data: UserCreate) -> User:
    if UserRepo.get_user_by_email(db, data.email) is not None:
        raise ValueError("Email is already in use")
    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password_hash="TEMP-NOT-A-REAL-HASH"
    )
    return UserRepo.create_user(db, user)

def get_user(db: Session, user_id: int) -> User | None:
    return UserRepo.get_user_by_id(db, user_id)