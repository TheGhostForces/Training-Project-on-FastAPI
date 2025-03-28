from datetime import datetime
from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from repository import UserRepository, ChatRepository


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # username -> WebSocket

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, websocket: WebSocket, username: str):
        if username in self.active_connections:
            del self.active_connections[username]

    async def send_personal_message(
            self,
            message_text: str,
            sender_username: str,
            receiver_username: str,
            timestamp: str
    ):
        if receiver_username in self.active_connections:
            connection = self.active_connections[receiver_username]
            await connection.send_json({
                "text": message_text,
                "sender": sender_username,
                "timestamp": timestamp
            })

        if sender_username in self.active_connections:
            connection = self.active_connections[sender_username]
            await connection.send_json({
                "text": message_text,
                "receiver": receiver_username,
                "timestamp": timestamp,
                "is_own": True
            })

manager = ConnectionManager()

router = APIRouter(
    prefix="/chat",
)

@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket, username)
    try:
        while True:
            data = await websocket.receive_json()
            message_text = data.get("text")
            receiver_username = data.get("receiver_username")

            if not message_text or not receiver_username:
                await websocket.send_json({"error": "Invalid message format"})
                continue

            sender = await UserRepository.find_user_by_username(username)
            if not sender:
                await websocket.send_json({"error": "Sender not found"})
                continue

            await ChatRepository.save_message(message_text,sender.id, receiver_username)

            await manager.send_personal_message(
                message_text=message_text,
                sender_username=username,
                receiver_username=receiver_username,
                timestamp=datetime.now().isoformat()
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, username)