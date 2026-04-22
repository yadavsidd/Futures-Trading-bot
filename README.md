# Binance Futures Trading Bot 🤖

A Python CLI trading bot for the **Binance Futures Demo API** (`demo-fapi.binance.com`).
Supports MARKET, LIMIT, and STOP_LIMIT orders with full input validation, structured logging, and an interactive terminal UI.

---

## Setup

### 1. Clone & enter the directory
```bash
git clone <your-repository-url>
cd trading_bot
```

### 2. Create your `.env`
```bash
cp .env.example .env
# Edit .env and fill in your Demo API credentials from demo-fapi.binance.com
```

### 3. Create virtualenv & install dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> ⚠️ Never commit `.env` — it is already in `.gitignore`.

---

## Running the Bot

### Option A — Interactive TUI (recommended)
```bash
python tui.py
```
Launches a full interactive terminal UI with:
- ASCII banner and numbered menu
- Step-by-step prompts with inline validation
- Order confirmation before any API call
- Animated spinner during requests
- Colour-coded result panels (🟢 FILLED / 🟡 NEW / 🔴 error)
- Live log viewer (last 20 entries)

### Option B — One-shot CLI
Place orders directly without any interactive prompts:

| Order Type | Command |
|------------|---------|
| MARKET BUY | `python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.05` |
| MARKET SELL | `python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 1.5` |
| LIMIT BUY | `python cli.py --symbol BNBUSDT --side BUY --type LIMIT --quantity 5.0 --price 76000` |
| STOP_LIMIT BUY | `python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 1.0 --price 76000 --stop-price 76500` |

Check an existing order by ID:
```bash
python cli.py get-order --symbol BTCUSDT --order-id 13060790564
```

Validation error example (missing price for LIMIT):
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 1
# Error: Price is required for LIMIT orders.
```

---

## Project Structure

```text
trading_bot/
├── .env.example          # Credential template
├── .env                  # Your secrets (gitignored)
├── .gitignore
├── requirements.txt
├── README.md
├── run.md                # Evaluation & verification guide
├── tui.py                # Interactive terminal UI (recommended entry point)
├── cli.py                # One-shot CLI (scriptable)
├── logs/
│   ├── sample_market.log # Sample MARKET order output
│   └── sample_limit.log  # Sample LIMIT order output
└── bot/
    ├── __init__.py       # Module docstring
    ├── client.py         # BinanceClient + APIError / NetworkError
    ├── logging_config.py # Dual console+file logger
    ├── orders.py         # place_market / place_limit / place_stop_limit / get_order
    └── validators.py     # Symbol, side, type, qty, price, stop_price validators
```

---

## Order Types

| Type | Required flags | Notes |
|------|---------------|-------|
| `MARKET` | symbol, side, quantity | Executes immediately at market price |
| `LIMIT` | symbol, side, quantity, price | Stays open until price is hit; GTC |
| `STOP_LIMIT` | symbol, side, quantity, price, stop-price | Triggers at stop-price, fills at price |

> **Price tip**: Use realistic prices close to the current market. Binance rejects prices outside its allowed range.

---

## Logging

On first run, `trading_bot.log` is created in the project root:
- **Console** → `INFO` level (order placed / filled)
- **File** → `DEBUG` level (full signed request params + raw response body)

Log is appended across runs — never overwritten.

---

## Assumptions
- Targets **Binance Futures Demo API** (`https://demo-fapi.binance.com`)
- Only **USDT-M** pairs are accepted (symbols must end in `USDT`)
- All LIMIT and STOP_LIMIT orders use `timeInForce = GTC`
- Credentials are HMAC-SHA256 signed on every request
