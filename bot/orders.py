"""
Business Logic Layer for placing and processing orders.
Coordinates validations, API client interactions, and response mapping.
"""

import logging
from typing import Optional
from bot.client import BinanceFuturesClient
from bot.models import OrderRequest, OrderResult
from bot.config import Config
from bot.validators import validate_order_params

logger = logging.getLogger(__name__)


class OrderProcessor:
    """
    Handles business rules for placing orders on Binance Futures.
    Uses Dependency Injection for the Binance API client.
    """

    def __init__(self, client: Optional[BinanceFuturesClient] = None):
        """
        Initializes the OrderProcessor.
        If no client is provided, builds one using active Config settings.
        """
        # Validate that configurations are loaded correctly
        Config.validate()
        
        self.client = client or BinanceFuturesClient(
            api_key=Config.BINANCE_API_KEY,
            api_secret=Config.BINANCE_SECRET_KEY,
            use_testnet=Config.USE_TESTNET
        )

    def execute_order(self, request: OrderRequest) -> OrderResult:
        """
        Executes a validated OrderRequest.
        Calls the appropriate client method and returns a normalized OrderResult.
        """
        logger.info(
            "Processing validated order request: Symbol=%s, Side=%s, Type=%s, Qty=%s",
            request.symbol, request.side, request.order_type, request.quantity
        )

        # Place the order via client based on type
        if request.order_type == "MARKET":
            raw_response = self.client.place_market_order(
                symbol=request.symbol,
                side=request.side,
                quantity=request.quantity
            )
        elif request.order_type == "LIMIT":
            if request.price is None:
                raise ValueError("LIMIT orders require a price.")
            raw_response = self.client.place_limit_order(
                symbol=request.symbol,
                side=request.side,
                quantity=request.quantity,
                price=request.price
            )
        else:
            raise ValueError(f"Unsupported order type: {request.order_type}")

        # Parse and normalize raw API response
        logger.debug("Parsing raw response into normalized OrderResult")
        result = OrderResult.from_binance_response(raw_response)
        
        logger.info(
            "Order executed successfully: OrderID=%s, Status=%s, AvgPrice=%s",
            result.order_id, result.status, result.avg_price
        )
        return result

    def prepare_and_execute(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> OrderResult:
        """
        Validates raw arguments, creates an OrderRequest, and executes the order.
        """
        logger.info("Received order request from external interface")
        
        # 1. Run local validation layer
        validated_params = validate_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        # 2. Build OrderRequest model
        request = OrderRequest(
            symbol=validated_params["symbol"],
            side=validated_params["side"],
            order_type=validated_params["type"],
            quantity=validated_params["quantity"],
            price=validated_params["price"]
        )
        
        # 3. Process order
        return self.execute_order(request)
