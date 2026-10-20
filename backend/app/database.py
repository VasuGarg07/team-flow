from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from .config import app_settings

engine = create_engine(url=app_settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db() -> Generator[Session, None, None]:
    try:
        session = SessionLocal()
        yield session
    finally:
        session.close()

class Base(DeclarativeBase):
    pass