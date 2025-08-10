# worker.py (processing function)
import math
from service.app.scanner import fetch_ohlcv
from service.app.risk import fee_check, compute_position_size
from service.app.executor import place_order
from service.app.config import settings

def process_signal_and_execute(payload: dict):
    """
    payload expected keys:
      - symbol (e.g., 'BTC/USDT' or 'BTCUSDT')
      - action: 'buy' or 'sell'
      - timeframe: '5m' (optional)
      - signal_id: unique id from TradingView if available (optional)
    """
    symbol = payload.get('symbol')
    if not symbol:
        symbol = payload.get('ticker') or payload.get('instrument')
    # normalize symbol for CCXT e.g., BTC/USDT
    if '/' not in symbol:
        if symbol.endswith('USDT'):
            symbol_norm = symbol[:-4] + '/USDT'
        else:
            symbol_norm = symbol
    else:
        symbol_norm = symbol

    action = payload.get('action','buy').lower()
    tf = payload.get('timeframe','5m')
    signal_id = payload.get('signal_id') or payload.get('id')

    # 1) fetch fresh 5m candles and recompute indicators (scanner.fetch_ohlcv returns DataFrame)
    df = fetch_ohlcv(symbol_norm, timeframe=tf, limit=200)

    # Here implement the same rules as Pine:
    # compute supertrend, rsi, rsi sma etc. For brevity assume scanner exposes a function 'strategy_signal'
    from service.app.scanner import strategy_signal  # implement same logic there
    validated = strategy_signal(df)  # returns True/False and expected_return_pct

    if not validated['valid']:
        # don't trade; log/notify
        return {'status':'rejected','reason':'validation_failed','details':validated}

    expected_return = validated['expected_return']  # fraction, e.g., 0.005 for 0.5%

    # 2) fee check
    ok, details = fee_check(symbol_norm, expected_return)
    if not ok:
        return {'status':'rejected','reason':'fee_check_failed','details':details}

    # 3) position size (in base currency amount). compute_position_size returns amount in base units
    amount = compute_position_size(symbol_norm, settings.max_position_pct)
    if amount <= 0:
        return {'status':'rejected','reason':'position_size_zero'}

    # 4) place order (market by default). If you prefer limit, you can compute a price
    if settings.trading_enabled:
        try:
            order = place_order(symbol_norm, action, amount, order_type='market', signal_id=signal_id)
            return {'status':'placed','order':order}
        except Exception as e:
            return {'status':'error','error':str(e)}
    else:
        # dry-run mode
        return {'status':'simulated','symbol':symbol_norm,'side':action,'amount':amount}
