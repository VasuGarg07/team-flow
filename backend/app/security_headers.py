from collections.abc import Awaitable, Callable

from fastapi import Request, Response

from app.config import app_settings

DOC_PATHS = ("/docs", "/redoc", "/openapi.json")


async def add_security_headers(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    if not request.url.path.startswith(DOC_PATHS):
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    if request.url.path.startswith("/auth"):
        response.headers["Cache-Control"] = "no-store"
    if app_settings.COOKIE_SECURE:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response