from fastapi import FastAPI
from .webhook import router as webhook_router

app = FastAPI(title="TradingView -> Binance Bot")
app.include_router(webhook_router, prefix="/webhook")

@app.get("/health")
def health():
    return {"status": "ok"}
