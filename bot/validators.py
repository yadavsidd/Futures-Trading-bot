import logging
from typing import Optional

logger = logging.getLogger("trading_bot")

def validate_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if not symbol.endswith("USDT"):
        raise ValueError(f"Invalid symbol: {symbol}. Must end with USDT.")
    logger.debug(f"Validated symbol: {symbol}")
    return symbol


def validate_side(side: str) -> str:
    side = side.upper()
    if side not in ("BUY", "SELL"):
        raise ValueError(f"Invalid side: {side}. Must be BUY or SELL.")
    logger.debug(f"Validated side: {side}")
    return side


def validate_order_type(order_type: str) -> str:
    order_type = order_type.upper()
    if order_type not in ("MARKET", "LIMIT", "STOP_LIMIT", "STOP"):
        raise ValueError(f"Invalid order_type: {order_type}. Must be MARKET, LIMIT, or STOP_LIMIT.")
    logger.debug(f"Validated order_type: {order_type}")
    return order_type


def validate_quantity(qty: str) -> float:
    try:
        qty_float = float(qty)
    except ValueError:
        raise ValueError(f"Invalid quantity: {qty}. Must be a valid float.")
        
    if qty_float <= 0:
        raise ValueError(f"Invalid quantity: {qty}. Must be greater than 0.")
        
    logger.debug(f"Validated quantity: {qty_float}")
    return qty_float


def validate_price(price: str | None, order_type: str) -> float | None:
    order_type_upper = order_type.upper()
    
    if order_type_upper in ("LIMIT", "STOP_LIMIT", "STOP"):
        if price is None:
            raise ValueError(f"Price is required for {order_type_upper} orders.")
        
        try:
            price_float = float(price)
        except ValueError:
            raise ValueError(f"Invalid price: {price}. Must be a valid float.")
            
        if price_float <= 0:
            raise ValueError(f"Invalid price: {price}. Must be greater than 0.")
            
        logger.debug(f"Validated price: {price_float} for {order_type_upper} order")
        return price_float
        
    elif order_type_upper == "MARKET":
        logger.debug(f"Validated price: ignored for MARKET order")
        return None
    else:
        # Extra safety check, though validate_order_type typically handles this
        raise ValueError(f"Unknown order type: {order_type}")

def validate_stop_price(stop_price: str | None, order_type: str) -> float | None:
    order_type_upper = order_type.upper()
    
    if order_type_upper in ("STOP_LIMIT", "STOP"):
        if stop_price is None:
            raise ValueError("Stop price is required for STOP_LIMIT orders.")
        
        try:
            price_float = float(stop_price)
        except ValueError:
            raise ValueError(f"Invalid stop price: {stop_price}. Must be a valid float.")
            
        if price_float <= 0:
            raise ValueError(f"Invalid stop price: {stop_price}. Must be greater than 0.")
            
        logger.debug(f"Validated stop price: {price_float} for STOP_LIMIT order")
        return price_float
        
    else:
        logger.debug(f"Validated stop price: ignored for {order_type_upper} order")
        return None
