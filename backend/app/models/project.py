from datetime import datetime

from sqlalchemy import ForeignKey, String, func

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
