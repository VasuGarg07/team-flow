import asyncio
import json

from fastapi import WebSocket
from redis import RedisError
from redis.asyncio import Redis as AsyncRedis

from app.cache import redis_client
from app.config import app_settings


class ConnectionManager:

    def __init__(self) -> None:
        self.rooms: dict[int, set[WebSocket]] = {}

    def join_room(self, workspace_id: int, websocket: WebSocket) -> None:
        if workspace_id not in self.rooms:
            self.rooms[workspace_id] = set()
        self.rooms[workspace_id].add(websocket)

    def leave_room(self, workspace_id: int, websocket: WebSocket) -> None:
        room = self.rooms.get(workspace_id)
        if not room:
            return
        room.discard(websocket)
        if len(room) == 0:
            del self.rooms[workspace_id]

    async def broadcast(self, workspace_id: int, text: str) -> None:
        room = self.rooms.get(workspace_id)
        if not room:
            return
        for websocket in list(room):
            try:
                await websocket.send_text(text)
            except Exception:
                self.leave_room(workspace_id, websocket)


connection_manager = ConnectionManager()


def publish_event(workspace_id: int, event: dict[str, object]) -> None:
    try:
        redis_client.publish(f"events:workspace:{workspace_id}", json.dumps(event))
    except RedisError:
        pass


async def listen_for_events() -> None:
    while True:
        try:
            client = AsyncRedis.from_url(app_settings.REDIS_URL, decode_responses=True)
            pubsub = client.pubsub()
            await pubsub.psubscribe("events:workspace:*")
            async for message in pubsub.listen():
                if message["type"] != "pmessage":
                    continue
                workspace_id = int(message["channel"].split(":")[-1])
                await connection_manager.broadcast(workspace_id, message["data"])
        except RedisError:
            await asyncio.sleep(5)