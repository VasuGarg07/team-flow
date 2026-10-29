import logging
from redis import Redis, RedisError
from rq import Queue, Retry

from app.config import app_settings
from app.jobs import send_assignment_notification


queue_connection = Redis.from_url(app_settings.REDIS_URL)
task_queue = Queue("default", connection=queue_connection)
logger = logging.getLogger(__name__)

def enqueue_assignment_notification(task_id: int) -> None:
    try:
        task_queue.enqueue(send_assignment_notification, task_id, retry=Retry(
            max=3, interval=[10, 60, 300]), job_timeout=30)
    except RedisError:
        logger.exception("Could not enqueue the assignment notification")
