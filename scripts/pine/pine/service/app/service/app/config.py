import os
from dotenv import load_dotenv
load_dotenv()

BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")
BINANCE_TESTNET = os.getenv("BINANCE_TESTNET", "true").lower() in ("1","true","yes")
TV_WEBHOOK_SECRET = os.getenv("TV_WEBHOOK_SECRET", "changeme")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
TRADING_ENABLED = os.getenv("TRADING_ENABLED", "false").lower() in ("1","true","yes")
MAX_POSITION_PCT = float(os.getenv("MAX_POSITION_PCT", "0.001"))
SAFETY_MARGIN_PCT = float(os.getenv("SAFETY_MARGIN_PCT", "0.002"))
SLIPPAGE_PCT = float(os.getenv("SLIPPAGE_PCT", "0.001"))
DEFAULT_SYMBOL = os.getenv("DEFAULT_SYMBOL", "BTC/USDT")
