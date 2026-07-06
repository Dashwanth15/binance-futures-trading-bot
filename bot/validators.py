"""
Input validation functions for the Binance Futures Trading Bot.
Verifies all order parameters locally before sending requests to the API.
"""

import re
from bot.exceptions import ValidationError

# Regex to check symbol format (e.g., BTCUSDT, ETHUSDT)
# Usually Binance symbols are uppercase alphanumeric strings, typically 5 to 15 chars.
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{3,15}$")


def validate_symbol(symbol: str) -> str:
    """
    Validates the trading symbol format.
    Normalizes the symbol to uppercase.
    """
    if not isinstance(symbol, str):
        raise ValidationError("Trading symbol must be a string.")
        
    cleaned_symbol = symbol.strip().upper()
    if not cleaned_symbol:
        raise ValidationError("Trading symbol cannot be empty.")
        
    if not SYMBOL_PATTERN.match(cleaned_symbol):
        raise ValidationError(
            f"Invalid trading symbol format: '{symbol}'. "
            "Must be alphanumeric uppercase (e.g., BTCUSDT, ETHUSDT)."
        )
    return cleaned_symbol


def validate_side(side: str) -> str:
    """
    Validates and normalizes the order side.
    Must be either 'BUY' or 'SELL'.
    """
    if not isinstance(side, str):
        raise ValidationError("Order side must be a string.")
        
    cleaned_side = side.strip().upper()
    if cleaned_side not in ("BUY", "SELL"):
        raise ValidationError(
            f"Invalid order side: '{side}'. Must be 'BUY' or 'SELL'."
        )
    return cleaned_side


def validate_order_type(order_type: str) -> str:
    """
    Validates and normalizes the order type.
    Must be either 'MARKET' or 'LIMIT'.
    """
    if not isinstance(order_type, str):
        raise ValidationError("Order type must be a string.")
        
    cleaned_type = order_type.strip().upper()
    if cleaned_type not in ("MARKET", "LIMIT"):
        raise ValidationError(
            f"Invalid order type: '{order_type}'. Must be 'MARKET' or 'LIMIT'."
        )
    return cleaned_type


def validate_quantity(quantity: float) -> float:
    """
    Validates the order quantity.
    Must be a positive float/int greater than zero.
    """
    try:
        val = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a valid number, got '{quantity}'.")
        
    if val <= 0:
        raise ValidationError(f"Quantity must be greater than zero. Got {val}.")
        
    return val


def validate_price(order_type: str, price: float | None) -> float | None:
    """
    Validates the price based on the order type.
    For LIMIT orders: price is required and must be > 0.
    For MARKET orders: price should be None.
    """
    cleaned_type = order_type.strip().upper()
    
    if cleaned_type == "LIMIT":
        if price is None:
            raise ValidationError("LIMIT orders require a price.")
        try:
            val = float(price)
        except (ValueError, TypeError):
            raise ValidationError(f"Price must be a valid number, got '{price}'.")
            
        if val <= 0:
            raise ValidationError(f"Price must be greater than zero. Got {val}.")
        return val
        
    elif cleaned_type == "MARKET":
        if price is not None:
            raise ValidationError("MARKET orders do not accept a price.")
        return None
        
    return None


def validate_order_params(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None
) -> dict:
    """
    Orchestrates validation of all order parameters.
    Returns a dictionary of validated and normalized parameters.
    Raises ValidationError if any parameter is invalid.
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_type = validate_order_type(order_type)
    validated_qty = validate_quantity(quantity)
    validated_price = validate_price(validated_type, price)
    
    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "type": validated_type,
        "quantity": validated_qty,
        "price": validated_price,
    }
