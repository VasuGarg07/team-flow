from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import ContentType


class AttachmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_name: str
    content_type: ContentType
    size_bytes: int
    uploaded_by: int
    created_at: datetime