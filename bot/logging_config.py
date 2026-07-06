"""
Logging configuration for the Binance Futures Trading Bot.
Sets up file rotation and console logging handlers.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_level: int = logging.INFO) -> None:
    """
    Sets up python logging configuration.
    Creates a 'logs/' directory if it doesn't exist.
    Configures console handler and a rotating file handler.
    """
    # 1. Determine logs folder and create it
    # Workspace root is parent of 'bot' directory
    workspace_dir = Path(__file__).resolve().parent.parent
    logs_dir = workspace_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / "trading_bot.log"

    # 2. Define formats
    # Standard format: timestamp [LEVEL] LoggerName (filename:line): message
    log_format = "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    formatter = logging.Formatter(log_format)

    # 3. Create Handlers
    # Rotating File Handler: Max 5MB per log file, keeping 5 backup files
    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)  # File gets detailed logs

    # Console Handler: Standard output for CLI visibility
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)  # CLI gets configured level (default INFO)

    # 4. Configure Root Logger
    root_logger = logging.getLogger()
    # Ensure root logger passes all levels down to handlers
    root_logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers if setup_logging is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 5. Mute verbose external libraries to prevent log spam
    # For example, urllib3, websockets, and python-binance's HTTP client
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    # python-binance has some internal loggers that can be noisy
    logging.getLogger("binance").setLevel(logging.WARNING)

    # Log application startup details
    logging.getLogger(__name__).info(
        "Logging configured. Console level: %s, File target: %s",
        logging.getLevelName(log_level),
        log_file
    )
