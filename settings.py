import redis.asyncio as redis
import os
from dotenv import load_dotenv

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SECRET_KEY")
redis_url = os.getenv("REDIS_URL")
r = redis.Redis(host='localhost', port=6379, decode_responses=True)