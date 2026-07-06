"""
CLI entry point for the Binance Futures Trading Bot.
Provides both direct CLI command execution and an interactive command mode.
Uses Typer for command definition and formatting.
"""

import sys
from pathlib import Path

# Ensure the project root is in sys.path so 'bot' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datetime import datetime
import logging
from typing import Optional

import typer
from bot.config import Config
from bot.exceptions import BotError, ConfigError, ValidationError, BinanceAPIError, NetworkError
from bot.logging_config import setup_logging
from bot.models import OrderRequest, OrderResult
from bot.orders import OrderProcessor
from bot.validators import (
    validate_order_params,
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)

# Create the Typer app
app = typer.Typer(
    name="binance-futures-bot",
    help="A CLI Trading Bot to place Market and Limit orders on Binance USDT-M Futures Testnet.",
    add_completion=False
)

logger = logging.getLogger("bot.cli")


def print_order_summary(symbol: str, side: str, order_type: str, quantity: float, price: Optional[float] = None) -> None:
    """Prints a styled order summary to the console before placement."""
    typer.echo("=" * 40)
    typer.secho("Order Summary", fg=typer.colors.CYAN, bold=True)
    typer.echo("=" * 40)
    
    # Grid layout for summary
    typer.echo(f"{'Symbol:':<16} {symbol}")
    typer.echo(f"{'Side:':<16} {side}")
    typer.echo(f"{'Type:':<16} {order_type}")
    typer.echo(f"{'Quantity:':<16} {quantity}")
    if order_type == "LIMIT":
        typer.echo(f"{'Price:':<16} {price}")
    else:
        typer.echo(f"{'Price:':<16} N/A (Market Order)")
    typer.echo("=" * 40)


def print_success_details(result: OrderResult) -> None:
    """Prints a styled success details block after order execution."""
    typer.secho("Order Successful!", fg=typer.colors.GREEN, bold=True)
    typer.echo("-" * 40)
    typer.echo(f"{'Order ID:':<20} {result.order_id}")
    typer.echo(f"{'Status:':<20} {result.status}")
    typer.echo(f"{'Side:':<20} {result.side}")
    typer.echo(f"{'Order Type:':<20} {result.order_type}")
    typer.echo(f"{'Executed Qty:':<20} {result.executed_qty}")
    typer.echo(f"{'Average Price:':<20} {result.avg_price}")
    
    time_str = result.execution_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    typer.echo(f"{'Execution Time:':<20} {time_str}")
    typer.echo("-" * 40)


def print_failure_details(error_type: str, reason: str, details: Optional[str] = None) -> None:
    """Prints a styled failure details block to stdout."""
    typer.secho("Order Failed!", fg=typer.colors.RED, bold=True)
    typer.secho(f"Reason: {reason}", fg=typer.colors.YELLOW)
    if details:
        typer.echo(f"Details: {details}")
    typer.echo("=" * 40)


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging (sets logger level to DEBUG)."
    )
):
    """
    Callback to run before any command. Sets up log configurations based on options.
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    setup_logging(log_level=log_level)
    logger.info("Application starting up...")


@app.command()
def place_order(
    symbol: str = typer.Option(
        ..., "--symbol", "-s", help="The trading pair symbol (e.g. BTCUSDT, ETHUSDT)."
    ),
    side: str = typer.Option(
        ..., "--side", "-d", help="Order direction: BUY or SELL."
    ),
    order_type: str = typer.Option(
        ..., "--type", "-t", help="Order type: MARKET or LIMIT."
    ),
    quantity: float = typer.Option(
        ..., "--quantity", "-q", help="The quantity of the asset to trade."
    ),
    price: Optional[float] = typer.Option(
        None, "--price", "-p", help="Price for LIMIT orders. Required if order type is LIMIT."
    ),
    confirm: bool = typer.Option(
        True, "--confirm/--no-confirm", help="Prompt for confirmation before sending the order."
    )
):
    """
    Place a Market or Limit order directly on Binance USDT-M Futures Testnet.
    """
    # 1. Log request arrival
    logger.info(
        "Incoming CLI order request: Symbol=%s, Side=%s, Type=%s, Qty=%s, Price=%s",
        symbol, side, order_type, quantity, price
    )

    try:
        # Load and validate config before moving further
        Config.validate()
        processor = OrderProcessor()
    except ConfigError as ce:
        logger.error("Configuration validation failed: %s", ce)
        typer.secho(f"Configuration Error: {ce}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Failed during initialization")
        typer.secho(f"Initialization Error: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)

    # 2. Local validation check
    try:
        # Local validation ensures no invalid parameters hit the API
        validated = validate_order_params(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        logger.info("CLI input validated successfully: %s", validated)
    except ValidationError as ve:
        logger.warning("Local parameter validation failed: %s", ve)
        typer.secho(f"Validation Error: {ve}", fg=typer.colors.RED, err=True)
        sys.exit(1)

    # 3. Print order summary for review
    print_order_summary(
        symbol=validated["symbol"],
        side=validated["side"],
        order_type=validated["type"],
        quantity=validated["quantity"],
        price=validated["price"]
    )

    # 4. Confirmation dialog (Bonus feature)
    if confirm:
        if not typer.confirm("Do you want to submit this order to Binance Futures Testnet?"):
            logger.info("Order submission cancelled by user.")
            typer.echo("Order cancelled.")
            sys.exit(0)

    # 5. Place order and handle exceptions
    typer.echo("Submitting order...")
    logger.info("Sending order request to business logic layer...")
    
    try:
        # Build request model
        req = OrderRequest(
            symbol=validated["symbol"],
            side=validated["side"],
            order_type=validated["type"],
            quantity=validated["quantity"],
            price=validated["price"]
        )
        
        result = processor.execute_order(req)
        
        # Display Success
        print_success_details(result)
        
    except ValidationError as ve:
        logger.warning("Business layer validation error: %s", ve)
        print_failure_details("ValidationError", str(ve))
        sys.exit(1)
    except BinanceAPIError as bae:
        logger.error("Binance API returned error: %s", bae)
        print_failure_details("BinanceAPIError", bae.message, f"Code: {bae.code}, HTTP Status: {bae.status_code}")
        sys.exit(1)
    except NetworkError as ne:
        logger.error("Network connectivity issue: %s", ne)
        print_failure_details("NetworkError", ne.message, "Please check your internet connection and Binance service status.")
        sys.exit(1)
    except BotError as be:
        logger.error("General bot logic error: %s", be)
        print_failure_details("BotError", be.message)
        sys.exit(1)
    except Exception as e:
        logger.critical("Unhandled unexpected error: %s", e, exc_info=True)
        print_failure_details("UnexpectedError", f"An unexpected runtime error occurred: {e}")
        sys.exit(1)


@app.command()
def interactive():
    """
    Launch an interactive session that guides you through placing an order. (Bonus Feature)
    """
    typer.secho("=== Interactive Binance Futures Testnet Order Mode ===", fg=typer.colors.MAGENTA, bold=True)
    
    # Validate configuration and connectivity first
    try:
        Config.validate()
        processor = OrderProcessor()
        # Verify connectivity by pinging
        typer.echo("Checking connection to Binance Futures Testnet...")
        if not processor.client.ping():
            typer.secho("Warning: Unable to ping Binance Futures Testnet. Continuing anyway...", fg=typer.colors.YELLOW)
        else:
            typer.secho("Connected to Binance Futures Testnet.", fg=typer.colors.GREEN)
            
        # Validate keys via small authenticated API call (skip if using mock keys for testing)
        if "mock" in Config.BINANCE_API_KEY.lower():
            typer.secho("Mock credentials detected - skipping API credentials validation check.", fg=typer.colors.YELLOW)
        else:
            processor.client.validate_credentials()
    except ConfigError as ce:
        logger.error("Interactive config validation failed: %s", ce)
        typer.secho(f"\nConfiguration Error: {ce}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    except BotError as be:
        logger.error("Interactive initial connection failed: %s", be)
        typer.secho(f"\nConnection Error: {be}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected interactive mode startup error")
        typer.secho(f"\nStartup Error: {e}", fg=typer.colors.RED, err=True)
        sys.exit(1)

    # Prompt Loop: Symbol
    symbol = ""
    while True:
        try:
            raw_sym = typer.prompt("Enter trading pair (e.g. BTCUSDT)")
            symbol = validate_symbol(raw_sym)
            break
        except ValidationError as ve:
            typer.secho(f"Invalid input: {ve}", fg=typer.colors.RED)

    # Prompt Loop: Side
    side = ""
    while True:
        try:
            raw_side = typer.prompt("Enter side (BUY or SELL)")
            side = validate_side(raw_side)
            break
        except ValidationError as ve:
            typer.secho(f"Invalid input: {ve}", fg=typer.colors.RED)

    # Prompt Loop: Type
    order_type = ""
    while True:
        try:
            raw_type = typer.prompt("Enter order type (MARKET or LIMIT)")
            order_type = validate_order_type(raw_type)
            break
        except ValidationError as ve:
            typer.secho(f"Invalid input: {ve}", fg=typer.colors.RED)

    # Prompt Loop: Quantity
    quantity = 0.0
    while True:
        try:
            raw_qty = typer.prompt("Enter quantity (positive number)")
            quantity = validate_quantity(raw_qty)
            break
        except ValidationError as ve:
            typer.secho(f"Invalid input: {ve}", fg=typer.colors.RED)

    # Prompt Loop: Price (Only if LIMIT)
    price = None
    if order_type == "LIMIT":
        while True:
            try:
                raw_price = typer.prompt("Enter limit price (positive number)")
                price = validate_price(order_type, raw_price)
                break
            except ValidationError as ve:
                typer.secho(f"Invalid input: {ve}", fg=typer.colors.RED)

    # Display summary
    print_order_summary(symbol, side, order_type, quantity, price)

    # Confirmation
    if not typer.confirm("Do you want to submit this order to Binance Futures Testnet?"):
        logger.info("Interactive order cancelled by user.")
        typer.echo("Order cancelled.")
        sys.exit(0)

    # Place order
    typer.echo("Submitting order...")
    logger.info("Interactive submission: Symbol=%s, Side=%s, Type=%s, Qty=%s, Price=%s", symbol, side, order_type, quantity, price)
    
    try:
        req = OrderRequest(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        result = processor.execute_order(req)
        print_success_details(result)
    except BinanceAPIError as bae:
        logger.error("Binance API error in interactive mode: %s", bae)
        print_failure_details("BinanceAPIError", bae.message, f"Code: {bae.code}, HTTP Status: {bae.status_code}")
        sys.exit(1)
    except NetworkError as ne:
        logger.error("Network error in interactive mode: %s", ne)
        print_failure_details("NetworkError", ne.message)
        sys.exit(1)
    except Exception as e:
        logger.critical("Unhandled exception in interactive mode: %s", e, exc_info=True)
        print_failure_details("UnexpectedError", f"An unexpected runtime error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()
