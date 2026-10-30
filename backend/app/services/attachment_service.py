from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import ContentType, WorkspaceMember, Attachment, WorkspaceMemberRole
from app.errors import BadRequestError, ForbiddenError, NotFoundError
from app.services import task_service
from app.config import app_settings
from app.repositories import attachment_repository
from app.storage import delete_file, save_file


CHUNK_SIZE = 64 * 1024

MEDIA_TYPES = {
    ContentType.PNG: "image/png",
    ContentType.JPEG: "image/jpeg",
    ContentType.PDF: "application/pdf",
}

def read_limited(file: UploadFile, max_bytes: int) -> bytes:
    content = bytearray()
    while True:
        chunk = file.file.read(CHUNK_SIZE)
        if not chunk:
            break

        content.extend(chunk)
        if len(content) > max_bytes:
            raise BadRequestError("File is too large")

    return bytes(content)

def detect_type(content: bytes) -> tuple[ContentType, str]:
    if content.startswith(b"\x89PNG"):
        return ContentType.PNG, ".png"
    if content.startswith(b"\xff\xd8\xff"):
        return ContentType.JPEG, ".jpg"
    if content.startswith(b"%PDF-"):
        return ContentType.PDF, ".pdf"
    raise BadRequestError("Only PNG, JPG and PDF files are allowed")

def upload_attachment(db: Session, workspace_id: int, project_id: int, task_id: int, caller: WorkspaceMember, file: UploadFile) -> Attachment:
    task_service.get_task(db, workspace_id, project_id, task_id)
    content = read_limited(file, app_settings.MAX_UPLOAD_BYTES)
    content_type, extension = detect_type(content)
    stored_name = f"{uuid4().hex}{extension}"

    attachment = Attachment(
        task_id=task_id,
        uploaded_by=caller.user_id,
        original_name=Path(file.filename or "file").name[:200],
        stored_name=stored_name,
        content_type=content_type,
        size_bytes=len(content),
    )
    save_file(stored_name, content)
    try:
        return attachment_repository.create_attachment(db, attachment)
    except SQLAlchemyError:
        delete_file(stored_name)
        raise

def list_attachments(db: Session, workspace_id: int, project_id: int, task_id: int) -> list[Attachment]:
    task_service.get_task(db, workspace_id, project_id, task_id)
    return attachment_repository.list_attachments(db, task_id)


def get_attachment(db: Session, workspace_id: int, project_id: int, task_id: int, attachment_id: int) -> Attachment:
    task_service.get_task(db, workspace_id, project_id, task_id)
    attachment = attachment_repository.get_attachment(db, task_id, attachment_id)
    if attachment is None:
        raise NotFoundError("Attachment not found")
    return attachment


def delete_attachment(
    db: Session, workspace_id: int, project_id: int, task_id: int, attachment_id: int, caller: WorkspaceMember
) -> None:
    attachment = get_attachment(db, workspace_id, project_id, task_id, attachment_id)
    is_manager = caller.role in [WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN]
    if not (is_manager or attachment.uploaded_by == caller.user_id):
        raise ForbiddenError("You do not have access to do this")
    stored_name = attachment.stored_name
    attachment_repository.delete_attachment(db, attachment)
    delete_file(stored_name)
