import logging
import requests
from urllib.parse import urlencode
from bot.client import BinanceClient

logger = logging.getLogger("trading_bot")

def get_order(client, symbol: str, order_id: int) -> dict:
    """Fetch the current status of an order by its ID."""
    params = {
        "symbol": symbol,
        "orderId": order_id,
    }
    signed = client._sign_request(params)
    url = f"{client.base_url}/fapi/v1/order"
    headers = {"X-MBX-APIKEY": client.api_key}
    logger.debug(f"GET order {order_id} for {symbol}")
    try:
        response = requests.get(url, headers=headers, params=signed)
    except requests.exceptions.RequestException as e:
        from bot.client import NetworkError
        raise NetworkError(f"Network error: {e}") from e
    if response.status_code != 200:
        from bot.client import APIError
        raise APIError(response.text, response.status_code)
    return response.json()


def place_market_order(client: BinanceClient, symbol: str, side: str, quantity: float) -> dict:
    logger.info(f"Placing MARKET {side} order | Symbol: {symbol} | Qty: {quantity}")
    
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": str(quantity),
    }
    
    response = client._post("/fapi/v1/order", params)
    logger.info(f"MARKET order result | OrderID: {response.get('orderId')} | Status: {response.get('status')}")
    return response

def place_limit_order(client: BinanceClient, symbol: str, side: str, quantity: float, price: float) -> dict:
    logger.info(f"Placing LIMIT {side} order | Symbol: {symbol} | Qty: {quantity} | Price: {price}")
    
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "timeInForce": "GTC",
        "quantity": str(quantity),
        "price": str(price),
    }
    
    response = client._post("/fapi/v1/order", params)
    logger.info(f"LIMIT order result | OrderID: {response.get('orderId')} | Status: {response.get('status')}")
    return response

def place_stop_limit_order(client: BinanceClient, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> dict:
    logger.info(f"Placing STOP_LIMIT {side} order | Symbol: {symbol} | Qty: {quantity} | Price: {price} | StopPrice: {stop_price}")
    
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "timeInForce": "GTC",
        "quantity": str(quantity),
        "price": str(price),
        "stopPrice": str(stop_price),
    }
    
    response = client._post("/fapi/v1/order", params)
    logger.info(f"STOP_LIMIT order result | OrderID: {response.get('orderId')} | Status: {response.get('status')}")
    return response

def format_order_result(response: dict) -> str:
    order_id = response.get("orderId", "N/A")
    symbol = response.get("symbol", "N/A")
    status = response.get("status", "N/A")
    executed_qty = response.get("executedQty", "0")
    order_type = response.get("type", "N/A")
    side = response.get("side", "N/A")
    
    output = [
        "================== ORDER SUMMARY ==================",
        f"Order ID     : {order_id}",
        f"Symbol       : {symbol}",
        f"Type         : {order_type}",
        f"Side         : {side}",
        f"Status       : {status}",
        f"Executed Qty : {executed_qty}",
    ]
    
    if "avgPrice" in response:
        output.append(f"Avg Price    : {response['avgPrice']}")
        
    output.append("===================================================")
    
    return "\n".join(output)
