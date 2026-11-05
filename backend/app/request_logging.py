import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.logging_config import request_id_var

logger = logging.getLogger("app.requests")

async def log_requests(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    # Set Request Id ContextVar
    incoming_id = request.headers.get("X-Request-ID")
    if incoming_id is None or len(incoming_id) > 64:
        request_id = uuid.uuid4().hex
    else:
        request_id = incoming_id
    request_id_var.set(request_id)

    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 1)

    response.headers["X-Request-ID"] = request_id
    level = logging.WARNING if response.status_code >= 400 else logging.INFO
    logger.log(
        level,
        "request finished",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response
