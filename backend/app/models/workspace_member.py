from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from .user import User

class WorkspaceMemberRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[WorkspaceMemberRole] = mapped_column(default=WorkspaceMemberRole.MEMBER)
    user: Mapped[User] = relationship()