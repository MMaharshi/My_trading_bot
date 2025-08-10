from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
import json
import redis
from .config import REDIS_URL, TV_WEBHOOK_SECRET

router = APIRouter()
r = redis.from_url(REDIS_URL)
QUEUE_KEY = "tv:signals"

@router.post("/tradingview")
async def tradingview_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    # verify secret
    if payload.get("secret") != TV_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="unauthorized")
    # enqueue payload for worker
    r.rpush(QUEUE_KEY, json.dumps(payload))
    return {"status":"accepted"}
