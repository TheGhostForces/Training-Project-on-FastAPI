import settings
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from auth.security import get_current_user_from_token
from schemas import FeedBackAnswer, UserSchemaAdd

router = APIRouter(
    prefix="/feedback",
    tags=["FeedBack"]
)

@router.post("/send")
async def send_message(
        message: str,
        current_user: UserSchemaAdd = Depends(get_current_user_from_token)) -> FeedBackAnswer:
    try:
        await settings.r.publish("bot_channel", message)
        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def get_data_from_redis(redis_url, channel_name):
    redis = await settings.r.from_url(redis_url)
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel_name)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["type"] == "message":
                yield message["data"]
    finally:
        await pubsub.unsubscribe(channel_name)
        await pubsub.close()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    channel = "notifications"

    try:
        async for data in get_data_from_redis(settings.redis_url,channel):
            await websocket.send_text(data.decode("utf-8"))
    except WebSocketDisconnect:
        print("Client disconnected")