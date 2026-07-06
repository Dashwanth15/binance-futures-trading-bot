"""
Data models for the Binance Futures Trading Bot.
Uses dataclasses to provide type-safe representations of requests and responses.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass(frozen=True)
class OrderRequest:
    """Represents a validated request to place an order."""
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: float | None = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the order request to a standard dictionary."""
        data = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": self.quantity,
        }
        if self.price is not None:
            data["price"] = self.price
        return data


@dataclass(frozen=True)
class OrderResult:
    """Represents a normalized response returned after a successful order execution."""
    order_id: str
    symbol: str
    status: str
    side: str
    order_type: str
    executed_qty: float
    avg_price: float
    client_order_id: str
    execution_time: datetime
    raw_response: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_binance_response(cls, response: Dict[str, Any]) -> "OrderResult":
        """
        Parses a raw Binance futures API response and maps it to a normalized OrderResult.
        
        Binance Futures order response dictionary schema:
        {
            "orderId": 12345678,
            "symbol": "BTCUSDT",
            "status": "FILLED",
            "clientOrderId": "my_order_id",
            "price": "0.00",
            "avgPrice": "60000.50",
            "origQty": "0.001",
            "executedQty": "0.001",
            "side": "BUY",
            "type": "MARKET",
            "updateTime": 1625060000000,
            ...
        }
        """
        # Read fields safely with fallbacks
        order_id = str(response.get("orderId", ""))
        symbol = response.get("symbol", "").upper()
        status = response.get("status", "").upper()
        side = response.get("side", "").upper()
        order_type = response.get("type", "").upper()
        
        # Parse quantity and price
        try:
            executed_qty = float(response.get("executedQty", 0.0))
        except (ValueError, TypeError):
            executed_qty = 0.0
            
        try:
            # For LIMIT, it might return 'price', for MARKET/LIMIT avg price is in 'avgPrice'
            # If avgPrice is 0 or not set, fall back to price
            avg_price = float(response.get("avgPrice", 0.0))
            if avg_price == 0.0 and "price" in response:
                avg_price = float(response.get("price", 0.0))
        except (ValueError, TypeError):
            avg_price = 0.0
            
        client_order_id = response.get("clientOrderId", "")
        
        # Convert timestamp (millisecond epoch) to datetime
        update_time_ms = response.get("updateTime", 0)
        if update_time_ms:
            execution_time = datetime.fromtimestamp(update_time_ms / 1000.0, tz=timezone.utc)
        else:
            execution_time = datetime.now(timezone.utc)
            
        return cls(
            order_id=order_id,
            symbol=symbol,
            status=status,
            side=side,
            order_type=order_type,
            executed_qty=executed_qty,
            avg_price=avg_price,
            client_order_id=client_order_id,
            execution_time=execution_time,
            raw_response=response,
        )
