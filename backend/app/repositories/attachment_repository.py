from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Attachment


def create_attachment(db: Session, attachment: Attachment) -> Attachment:
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def list_attachments(db: Session, task_id: int) -> list[Attachment]:
    statement = select(Attachment).where(Attachment.task_id == task_id).order_by(Attachment.id)
    return list(db.scalars(statement).all())


def get_attachment(db: Session, task_id: int, attachment_id: int) -> Attachment | None:
    statement = select(Attachment).where(Attachment.task_id == task_id, Attachment.id == attachment_id)
    return db.scalar(statement)


def delete_attachment(db: Session, attachment: Attachment) -> None:
    db.delete(attachment)
    db.commit()