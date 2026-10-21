class AppError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_SERVER_ERROR"

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

class BadRequestError(AppError):
    status_code = 400
    code = "BAD_REQUEST"

class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHENTICATED"

class ForbiddenError(AppError):
    status_code = 403
    code = "FORBIDDEN"

class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"

class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"