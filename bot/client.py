"""
Binance Futures client wrapper.
Handles communication with the Binance USDT-M Futures Testnet API,
wraps exceptions, and manages authentication.
"""

import logging
from typing import Any, Dict
from binance import Client as BinanceClient
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException

from bot.exceptions import BinanceAPIError, NetworkError, ConfigError, ValidationError

logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """
    Wrapper around the python-binance Client specifically for USDT-M Futures on Testnet.
    Provides clean methods for market/limit order placement and handles exception mapping.
    """

    def __init__(self, api_key: str, api_secret: str, use_testnet: bool = True):
        """
        Initializes the Binance API Client.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.use_testnet = use_testnet
        
        try:
            # Initialize python-binance client
            logger.info("Initializing python-binance client (Testnet=%s)...", use_testnet)
            self._client = BinanceClient(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.use_testnet,
                requests_params={"timeout": 15}
            )
        except Exception as e:
            logger.exception("Failed to initialize python-binance Client")
            raise ConfigError(f"Failed to initialize Binance API Client: {e}")

    def ping(self) -> bool:
        """
        Pings the Binance Futures API to test connection.
        Returns True if successful, False otherwise.
        """
        try:
            logger.debug("Pinging Binance Futures API...")
            self._client.futures_ping()
            return True
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.warning("Ping failed: Binance exception: %s", e)
            return False
        except RequestException as e:
            logger.warning("Ping failed: Network exception: %s", e)
            return False

    def validate_credentials(self) -> None:
        """
        Validates the provided API key and secret by making an authenticated request.
        Raises ConfigError if credentials are unauthorized or invalid.
        """
        try:
            logger.debug("Validating Binance API credentials by fetching futures account info...")
            # We call a lightweight authenticated endpoint
            self._client.futures_account(recvWindow=5000)
            logger.info("Credentials validated successfully.")
        except BinanceAPIException as e:
            logger.error("Binance API Exception during credential validation: %s", e)
            # Binance code -2015 is invalid APIKey, code -1022 is invalid signature
            if e.code in (-2015, -1022) or e.status_code == 401:
                raise ConfigError(
                    "Invalid API credentials. Please double-check your API key and secret."
                ) from e
            raise BinanceAPIError(
                message=f"Binance API validation error: {e.message}",
                code=e.code,
                status_code=e.status_code
            ) from e
        except RequestException as e:
            logger.error("Network connection error during credential validation: %s", e)
            raise NetworkError(f"Network error trying to contact Binance API: {e}") from e
        except Exception as e:
            logger.error("Unexpected error during credential validation: %s", e)
            raise ConfigError(f"Failed to validate credentials: {e}") from e

    def place_market_order(self, symbol: str, side: str, quantity: float) -> Dict[str, Any]:
        """
        Places a MARKET order on USDT-M Futures.
        """
        logger.info(
            "Placing MARKET order: Symbol=%s, Side=%s, Qty=%s",
            symbol, side, quantity
        )
        return self._create_order(
            symbol=symbol,
            side=side,
            order_type="MARKET",
            quantity=quantity
        )

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        """
        Places a LIMIT order on USDT-M Futures.
        """
        logger.info(
            "Placing LIMIT order: Symbol=%s, Side=%s, Qty=%s, Price=%s",
            symbol, side, quantity, price
        )
        return self._create_order(
            symbol=symbol,
            side=side,
            order_type="LIMIT",
            quantity=quantity,
            price=price
        )

    def _create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None
    ) -> Dict[str, Any]:
        """
        Helper method that directly calls futures_create_order and wraps exceptions.
        """
        # Build arguments for futures_create_order
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity
        }

        # For LIMIT orders, price and timeInForce are mandatory on Binance Futures
        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = str(price)
            params["timeInForce"] = "GTC"  # Good 'Til Cancelled (standard default)

        try:
            logger.debug("Sending order request to Binance API with params: %s", params)
            response = self._client.futures_create_order(**params)
            logger.debug("Binance API raw response: %s", response)
            return response
        except BinanceAPIException as e:
            logger.error("Binance API Exception while placing order: %s", e)
            raise BinanceAPIError(
                message=e.message,
                code=e.code,
                status_code=e.status_code
            ) from e
        except BinanceRequestException as e:
            logger.error("Binance Request Exception while placing order: %s", e)
            raise ValidationError(f"Invalid request params for Binance: {e}") from e
        except RequestException as e:
            logger.error("Network Exception while placing order: %s", e)
            raise NetworkError(f"Network failure while connecting to Binance Futures API: {e}") from e
        except Exception as e:
            logger.critical("Unexpected error while placing order: %s", e)
            raise BinanceAPIError(f"Unexpected API client error: {e}") from e
