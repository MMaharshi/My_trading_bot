from .config import SAFETY_MARGIN_PCT, SLIPPAGE_PCT
from .executor import EXCHANGE

def get_fees_for_symbol(symbol):
    # conservative defaults
    return {'maker': 0.0005, 'taker': 0.001}

def fee_check(symbol, expected_return_pct):
    fees = get_fees_for_symbol(symbol)
    fee_entry = fees['taker']
    fee_exit = fees['taker']
    total_cost = fee_entry + fee_exit + SLIPPAGE_PCT
    allowed = expected_return_pct > (total_cost + SAFETY_MARGIN_PCT)
    details = {
        "expected_return": expected_return_pct,
        "fee_entry": fee_entry,
        "fee_exit": fee_exit,
        "slippage": SLIPPAGE_PCT,
        "total_cost": total_cost,
        "safety_margin": SAFETY_MARGIN_PCT,
        "allowed": allowed
    }
    return allowed, details

def compute_position_size(symbol, max_pct=0.001):
    bal = EXCHANGE.fetch_balance()
    usdt = 0.0
    try:
        usdt = float(bal.get('free', {}).get('USDT', 0) or bal.get('total', {}).get('USDT', 0) or 0)
    except Exception:
        usdt = 0.0
    ticker = EXCHANGE.fetch_ticker(symbol)
    price = float(ticker.get('last') or ticker.get('close') or 0)
    if price <= 0 or usdt <= 0:
        return 0.0
    usd_alloc = usdt * float(max_pct)
    amount = usd_alloc / price
    # round to 6 decimals to be safe
    return round(amount, 6)
