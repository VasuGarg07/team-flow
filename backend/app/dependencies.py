from collections.abc import Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WorkspaceMember, WorkspaceMemberRole
from app.errors import UnauthorizedError, NotFoundError, ForbiddenError
from app.security import decode_access_token
from app.repositories.user_repository import get_user_by_id
from app.repositories.workspace_repository import get_member

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    if credentials is None:
        raise UnauthorizedError("Missing token")

    user_id = decode_access_token(credentials.credentials)
    user = get_user_by_id(db, user_id)
    if user is None:
        raise UnauthorizedError("Invalid or expired token")

    return user

def require_workspace_role(*allowed_roles: WorkspaceMemberRole) -> Callable[..., WorkspaceMember]:
    def check_role(workspace_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> WorkspaceMember:
        member = get_member(db, workspace_id, current_user.id)
        if member is None:
            raise NotFoundError("Workspace not found")

        if member.role not in allowed_roles:
            raise ForbiddenError("You do not have permission to do this")

        return member

    return check_role