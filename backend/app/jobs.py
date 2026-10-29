from time import sleep

from app.database import SessionLocal
from app.models.task import Task

def send_assignment_notification(task_id: int) -> None:
    with SessionLocal() as db:
        task = db.get(Task, task_id)
        if task is None or task.assignee is None:
            return

        sleep(3)
        print(f"Sending email to {task.assignee.email}: you were assigned \"{task.name}\"")