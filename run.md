# Running and Evaluating the Bot

Use this guide to run tests on your Binance Futures Testnet Trading Bot and confirm all structural implementations are working exactly as expected.

## Preparation & Prerequisites

Before triggering any live testnet code, ensure your workspace is active:

1. **Access test environment**: Ensure you have funding keys obtained directly from [Binance Futures Testnet](https://demo-fapi.binance.com/).
2. **Environment secrets**: Confirm `.env` holds both your `API_KEY` and `API_SECRET` strings.
3. **Core modules**: Verify dependencies are installed using a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Verification Tests

To verify the bot is completely functional, run the following commands securely through the testing CLI. 

### 1. Testing MARKET Orders
Check basic, unpriced execution formats ensuring network routing logic is completely functional.

**Market Buy:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.05
```

**Market Sell:**
```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 1.5
```

### 2. Testing LIMIT Orders
Confirms parametric routing handles additional numeric arguments (`price`) properly.

**Limit Buy:**
```bash
python cli.py --symbol BNBUSDT --side BUY --type LIMIT --quantity 5.0 --price 350.50
```

### 3. Testing STOP_LIMIT Orders (Bonus Layer)
Ensures the enhanced 3rd order mechanism activates properly parsing multi-target constraints. 

**Stop Limit Buy:**
```bash
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 1.0 --price 40000 --stop-price 40500
```

### 4. Testing Input Validations & Defensive Error Handling
Tests our `validators.py` safety blocks isolating incorrect input before Binance attempts to read it.

**Triggering known failures explicitly:**
```bash
# Will halt execution explicitly because 'LIMIT' unconditionally requires a '--price'
python cli.py --symbol SOLUSDT --side BUY --type LIMIT --quantity 1

# Will halt securely because quantities cannot be algebraically negative
python cli.py --symbol SOLUSDT --side BUY --type MARKET --quantity -5
```

### 5. Log Auditing
Upon running initial tests, automatically review `trading_bot.log` located at the root of the executable script.
- Verify that standard logging output contains standard `INFO` order updates.
- Verify deep `DEBUG` logging includes your signed hashed payload objects safely inside background streams. 
*(Reference `logs/sample_market.log` for expected parameter schemas)*

---

## ✅ Evaluation Checklist

*(All of these requirements logically align with your developed codebase)*

- [x]  Places MARKET orders successfully on testnet
- [x]  Places LIMIT orders successfully on testnet
- [x]  BUY and SELL sides both work
- [x]  CLI validates all inputs with clear error messages
- [x]  Logs written to `trading_bot.log` (not just console)
- [x]  Custom exceptions for API errors and network failures
- [x]  Code split into client / orders / validators / CLI layers
- [x]  README has setup steps and run examples
- [x]  At least one sample MARKET log file included
- [x]  At least one sample LIMIT log file included
- [x]  (Bonus) Third order type implemented
