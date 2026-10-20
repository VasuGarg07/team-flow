from datetime import datetime

from sqlalchemy import String, func

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())