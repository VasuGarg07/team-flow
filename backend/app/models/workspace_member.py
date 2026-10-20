from enum import Enum

from sqlalchemy import ForeignKey, String

from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column

class WorkspaceMemberRole(str, Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), primary_key=True)
    role: Mapped[WorkspaceMemberRole] = mapped_column(default=WorkspaceMemberRole.MEMBER)