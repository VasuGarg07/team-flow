import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from starlette.concurrency import run_in_threadpool

from app.database import SessionLocal
from app.errors import UnauthorizedError
from app.repositories.workspace_repository import get_member
from app.security import decode_access_token
from app.realtime import connection_manager


def is_workspace_member(token: str, workspace_id: int) -> bool:
    try:
        user_id = decode_access_token(token)
    except UnauthorizedError:
        return False
    with SessionLocal() as db:
        return get_member(db, workspace_id, user_id) is not None

async def read_token_message(websocket: WebSocket) -> str | None:
    try:
        data = await asyncio.wait_for(websocket.receive_json(), timeout=5)
    except (asyncio.TimeoutError, WebSocketDisconnect, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    token = data.get('token')
    return token if isinstance(token, str) else None

router = APIRouter(tags=["realtime"])


@router.websocket("/ws/workspaces/{workspace_id}")
async def workspace_events(websocket: WebSocket, workspace_id: int) -> None:
    await websocket.accept()
    token = await read_token_message(websocket)
    allowed = token is not None and await run_in_threadpool(is_workspace_member, token, workspace_id)
    if not allowed:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    connection_manager.join_room(workspace_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connection_manager.leave_room(workspace_id, websocket)