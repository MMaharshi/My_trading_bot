import time, uuid
import ccxt
from .config import BINANCE_API_KEY, BINANCE_API_SECRET, BINANCE_TESTNET
from .notifier import notify_text

def create_exchange():
    ex = ccxt.binance({
        "apiKey": BINANCE_API_KEY or "",
        "secret": BINANCE_API_SECRET or "",
        "enableRateLimit": True
    })
    if BINANCE_TESTNET:
        try:
            ex.set_sandbox_mode(True)
        except Exception:
            # older ccxt or exchange may not support; ignore
            pass
    return ex

EXCHANGE = create_exchange()

def generate_client_id(prefix: str, signal_id: str=None):
    ts = int(time.time())
    if signal_id:
        cid = f"{prefix}-{signal_id}"
    else:
        cid = f"{prefix}-{ts}-{uuid.uuid4().hex[:6]}"
    return cid[:36]

def place_order(symbol, side, amount, price=None, order_type="market", signal_id=None):
    client_id = generate_client_id(symbol.replace("/",""), signal_id)
    params = {"newClientOrderId": client_id}
    side = side.lower()
    if side not in ("buy", "sell"):
        raise ValueError("side must be buy or sell")
    try:
        if order_type == "market":
            order = EXCHANGE.create_order(symbol, "market", side, amount, None, params)
        else:
            order = EXCHANGE.create_order(symbol, "limit", side, amount, price, params)
        notify_text(f"Order placed: {symbol} {side} {amount} id={order.get('id')}")
        return order
    except Exception as e:
        notify_text(f"Order error: {e}")
        raise

def fetch_balance():
    return EXCHANGE.fetch_balance()

def fetch_ticker(symbol):
    return EXCHANGE.fetch_ticker(symbol)
