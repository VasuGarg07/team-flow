from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.models import User
import app.repositories.user_repository as user_repository
from app.errors import ConflictError, NotFoundError
from app.security import hash_password


def create_user(db: Session, data: UserCreate) -> User:
    email = data.email.strip().lower()

    if user_repository.get_user_by_email(db, email) is not None:
        raise ConflictError("Email is already in use")

    user = User(
        first_name=data.first_name,
        last_name=data.last_name,
        email=email,
        password_hash=hash_password(data.password)
    )
    return user_repository.create_user(db, user)

def get_user(db: Session, user_id: int) -> User:
    user = user_repository.get_user_by_id(db, user_id)
    if user is None:
        raise NotFoundError("User not found")
    
    return user