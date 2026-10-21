from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User
from app.errors import ConflictError


def create_user(db: Session, user: User) -> User:
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise ConflictError("Email is already in use")

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

def get_user_by_email(db: Session, email: EmailStr) -> User | None:
    statement = select(User).where(User.email == email)
    return db.scalar(statement)