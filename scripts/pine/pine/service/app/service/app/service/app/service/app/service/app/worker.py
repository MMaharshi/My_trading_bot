import redis, json, time
from .config import REDIS_URL, TRADING_ENABLED, MAX_POSITION_PCT
from .scanner import fetch_ohlcv, strategy_signal
from .risk import fee_check, compute_position_size
from .executor import place_order

r = redis.from_url(REDIS_URL)
QUEUE_KEY = "tv:signals"

def run_worker():
    print("Worker started - waiting for signals...")
    while True:
        item = r.blpop(QUEUE_KEY, timeout=5)
        if not item:
            continue
        _, raw = item
        try:
            payload = json.loads(raw)
            process(payload)
        except Exception as e:
            print("Worker error:", e)

def process(payload):
    # normalize symbol
    symbol = payload.get("symbol") or payload.get("ticker") or payload.get("instrument") or "BTCUSDT"
    if "/" not in symbol and symbol.endswith("USDT"):
        symbol = symbol[:-4] + "/USDT"
    timeframe = payload.get("timeframe", "5m")
    action = payload.get("action", "BUY").lower()

    print("Processing signal", symbol, action)

    # fetch candles and validate signal by recomputing indicators
    df = fetch_ohlcv(symbol, timeframe=timeframe, limit=200)
    validated = strategy_signal(df)
    if not validated["valid"]:
        print("Signal rejected by strategy check")
        return

    exp_ret = validated.get("expected_return", 0.0)
    ok, details = fee_check(symbol, exp_ret)
    if not ok:
        print("Rejected by fee check:", details)
        return

    amount = compute_position_size(symbol, MAX_POSITION_PCT)
    if amount <= 0:
        print("Position size is zero - skipping")
        return

    if TRADING_ENABLED:
        try:
            order = place_order(symbol, action, amount, order_type="market", signal_id=payload.get("signal_id"))
            print("Order placed:", order)
        except Exception as e:
            print("Order error:", e)
    else:
        print("SIMULATED order:", {"symbol": symbol, "action": action, "amount": amount})
