from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

import app.services.attachment_service as attachment_service
from app.database import get_db
from app.dependencies import require_workspace_role
from app.models import Attachment, WorkspaceMember, WorkspaceMemberRole
from app.schemas.attachment import AttachmentRead
from app.storage import file_path

router = APIRouter(
    prefix="/workspaces/{workspace_id}/projects/{project_id}/tasks/{task_id}/attachments",
    tags=["attachments"],
)

require_any_member = require_workspace_role(
    WorkspaceMemberRole.OWNER, WorkspaceMemberRole.ADMIN, WorkspaceMemberRole.MEMBER
)


@router.post("", response_model=AttachmentRead, status_code=201)
def upload_attachment_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> Attachment:
    return attachment_service.upload_attachment(db, workspace_id, project_id, task_id, member, file)


@router.get("", response_model=list[AttachmentRead])
def list_attachments_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> list[Attachment]:
    return attachment_service.list_attachments(db, workspace_id, project_id, task_id)


@router.get("/{attachment_id}")
def download_attachment_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> FileResponse:
    attachment = attachment_service.get_attachment(db, workspace_id, project_id, task_id, attachment_id)
    return FileResponse(
        file_path(attachment.stored_name),
        media_type=attachment_service.MEDIA_TYPES[attachment.content_type],
        filename=attachment.original_name,
        content_disposition_type="attachment",
        headers={"X-Content-Type-Options": "nosniff"},
    )


@router.delete("/{attachment_id}", status_code=204)
def delete_attachment_endpoint(
    workspace_id: int,
    project_id: int,
    task_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    member: WorkspaceMember = Depends(require_any_member),
) -> None:
    attachment_service.delete_attachment(db, workspace_id, project_id, task_id, attachment_id, member)