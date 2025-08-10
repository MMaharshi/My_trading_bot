# Crypto Trading Bot (TradingView -> Binance)

This repo contains a minimal automated trading bot that:
- Receives TradingView alerts via webhook
- Recomputes indicators server-side (Supertrend + RSI + volume + price rules)
- Validates fees vs expected return
- Simulates or places orders via Binance (CCXT)

**First:** populate `.env` (see `.env.example`) and keep testnet keys until you're comfortable.

See `scripts/tv_alert_template.txt` for the TradingView alert JSON to use.
