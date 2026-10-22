from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models import WorkspaceMemberRole

class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class WorkspaceUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime

class WorkspaceMemberAdd(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=200)
    role: WorkspaceMemberRole = Field(default=WorkspaceMemberRole.MEMBER)

class WorkspaceMemberRoleUpdate(BaseModel):
    role: WorkspaceMemberRole = Field(default=WorkspaceMemberRole.MEMBER)

class WorkspaceMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    role: WorkspaceMemberRole