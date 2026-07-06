"""
Custom exception hierarchy for the Binance Futures Trading Bot.
All exceptions derive from the base class BotError.
"""

class BotError(Exception):
    """Base exception for all bot errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ConfigError(BotError):
    """Raised when environment variables or configurations are invalid/missing."""
    pass


class ValidationError(BotError):
    """Raised when order parameters fail validation checks."""
    pass


class BinanceAPIError(BotError):
    """
    Raised when the Binance API returns an error response.
    Wraps the status code, error message, and internal API error code.
    """
    def __init__(self, message: str, code: int | None = None, status_code: int | None = None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code

    def __str__(self) -> str:
        code_str = f" [Code: {self.code}]" if self.code is not None else ""
        status_str = f" (HTTP {self.status_code})" if self.status_code is not None else ""
        return f"{self.message}{code_str}{status_str}"


class NetworkError(BotError):
    """Raised when network operations fail, timeout, or DNS resolution fails."""
    pass
