"""
Configuration manager for the Binance Futures Trading Bot.
Loads and validates environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from bot.exceptions import ConfigError

# Load environment variables from .env file
# Search in the workspace directory (which is typically parent of the bot folder)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    """Class holding bot configurations."""
    
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "").strip()
    BINANCE_SECRET_KEY: str = os.getenv("BINANCE_SECRET_KEY", "").strip()
    
    # We default testnet to True for this assignment as required
    USE_TESTNET: bool = os.getenv("BINANCE_USE_TESTNET", "True").strip().lower() in ("true", "1", "yes")

    @classmethod
    def validate(cls) -> None:
        """
        Validates that required configurations are present.
        Raises ConfigError if anything is invalid or missing.
        """
        missing = []
        if not cls.BINANCE_API_KEY:
            missing.append("BINANCE_API_KEY")
        if not cls.BINANCE_SECRET_KEY:
            missing.append("BINANCE_SECRET_KEY")
            
        if missing:
            raise ConfigError(
                f"Missing required configuration environment variable(s): {', '.join(missing)}. "
                "Please make sure your .env file is configured correctly."
            )
            
        # Optional check: warn or raise if credentials appear to be placeholder strings
        if cls.BINANCE_API_KEY.startswith("your_") or cls.BINANCE_SECRET_KEY.startswith("your_"):
            raise ConfigError(
                "You are using the default placeholder credentials in your .env file. "
                "Please update them with your actual Binance Futures Testnet keys."
            )
