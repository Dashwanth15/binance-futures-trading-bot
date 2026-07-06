# Binance Futures Testnet Trading Bot

A clean, modular, production-grade Python command-line interface (CLI) trading bot to place Market and Limit orders on the Binance USDT-M Futures Testnet using the official `python-binance` library.

This application is built with a strict layered architecture, robust validation, structured exception handling, custom configurations, automated rotating logs, and an interactive CLI mode.

---

## Architecture Diagram

The project uses a layered architecture, where each layer has a single responsibility. Business logic, input validation, and external communications are completely decoupled.

```
       [ CLI Layer: cli.py ] 
                 │
                 ▼
     [ Validation Layer: bot/validators.py ] 
                 │
                 ▼
   [ Business Logic Layer: bot/orders.py ] 
                 │
                 ▼
    [ Binance Client Layer: bot/client.py ] 
                 │
                 ▼
       [ Binance Futures Testnet API ]
```

### Module Responsibilities:
1. **CLI Layer (`cli.py`)**: Uses `Typer` to handle user input parsing, console styling, interactive prompt loops, order summary visualization, and confirmation steps.
2. **Validation Layer (`bot/validators.py`)**: Validates input formatting, range limits, and logic constraints locally (e.g. `Quantity > 0`, price existence for `LIMIT` orders) *before* invoking API modules.
3. **Business Logic Layer (`bot/orders.py`)**: Coordinates validations, translates raw parameters into formal request models (`OrderRequest`), executes operations, and returns normalized output models (`OrderResult`).
4. **Binance Client Layer (`bot/client.py`)**: Handles configuration-driven client initialization, wraps third-party raw exceptions into domain-specific exception types, and interfaces directly with the Binance Futures Testnet REST API.

---

## Folder Structure

```
binance-futures-trading-bot/
├── bot/
│   ├── __init__.py           # Package initializer
│   ├── client.py             # Wrapper client around python-binance
│   ├── config.py             # Config manager loading credentials from env
│   ├── exceptions.py         # Custom application-specific exceptions
│   ├── logging_config.py     # Automatically configured logger with log rotation
│   ├── models.py             # Request & response representations (Dataclasses)
│   ├── orders.py             # Business logic processor layer
│   └── validators.py         # Local input parameters validation rules
├── logs/
│   └── trading_bot.log       # Automatically created rotating file log
├── cli.py                    # App entrypoint defining standard & interactive commands
├── .env.example              # Sample environment template
├── .gitignore                # Git files/folders ignore pattern
├── README.md                 # Project documentation
└── requirements.txt          # Third-party packages required
```

---

## Requirements & Installation

### Requirements
* Python 3.11+
* Operating System: Windows, macOS, or Linux
* A Binance Futures Testnet account (for generating API Keys)

### Setup & Installation

1. **Clone the repository** (or copy to your workspace):
   ```bash
   cd binance-futures-trading-bot
   ```

2. **Create and activate a virtual environment** (Recommended):
   ```bash
   # On Windows (PowerShell):
   python -m venv .venv
   .venv\Scripts\Activate.ps1

   # On macOS/Linux:
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Copy `.env.example` to `.env` and fill in your Binance Futures Testnet API credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` using your text editor:
   ```env
   BINANCE_API_KEY=your_binance_testnet_api_key_here
   BINANCE_SECRET_KEY=your_binance_testnet_secret_key_here
   ```

---

## How to Generate Binance Testnet API Keys

1. Navigate to the [Binance Futures Testnet website](https://testnet.binancefuture.com).
2. Log in using your credentials (or register a mock account using your email/social accounts).
3. Under the **API Key** section on the main dashboard, click on **API Key** or **Generate API Key**.
4. Save the generated **API Key** and **Secret Key** immediately, as the Secret Key will not be shown again.
5. Copy these values directly into your `.env` file.

---

## Running the Project

The CLI supports standard argument-based commands as well as an interactive user-friendly terminal prompt mode.

To see all options and automatic documentation:
```bash
python cli.py --help
```

### 1. Market Order Examples

Placing a MARKET order (price is not accepted, quantity is required):
```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

*Expected console output:*
```
========================================
Order Summary
========================================
Symbol:          BTCUSDT
Side:            BUY
Type:            MARKET
Quantity:        0.001
Price:           N/A (Market Order)
========================================
Do you want to submit this order to Binance Futures Testnet? [y/N]: y
Submitting order...
Order Successful!
----------------------------------------
Order ID:            347598273
Status:              FILLED
Side:                BUY
Order Type:          MARKET
Executed Qty:        0.001
Average Price:       61023.45
Execution Time:      2026-07-06 03:28:45 UTC
----------------------------------------
```

### 2. Limit Order Examples

Placing a LIMIT order (both price and quantity are required):
```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 62500.0
```

To skip the safety confirmation step, use the `--no-confirm` flag:
```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 62500.0 --no-confirm
```

---

## Bonus Feature: Interactive Mode

To run the application in a guided, interactive wizard style, run the following:
```bash
python cli.py interactive
```

This mode will:
1. Validate your `.env` configurations.
2. Establish a ping connection to Binance Futures Testnet to check connectivity.
3. Validate credentials with a lightweight authenticated call.
4. Prompt you step-by-step for the symbol, side, type, quantity, and price (only if Limit), validation checking inputs at each prompt before accepting them.
5. Display a final summary and ask for order confirmation before sending to Binance.

---

## Logging

Logging configurations are located in `bot/logging_config.py`. 

- **Automatic Log Creation**: The bot automatically creates a `logs/` directory and writes all transactions to `logs/trading_bot.log`.
- **Log Rotation**: Implements `RotatingFileHandler` with a file size limit of 5MB and 5 historical backups to prevent unlimited disk usage.
- **Log Format**: Includes Timestamp, Level, Logger/Module, Source code location, and Message.
- **Levels**: By default, logs write at the `INFO` level to the console, and `DEBUG` level to the log file. Use the global option `-v` / `--verbose` to set console logs to `DEBUG`.
- **Noise Control**: External libraries such as `requests`, `urllib3`, and `websockets` are automatically muted to `WARNING` level to preserve log readability.

---

## Error & Exception Handling

The application wraps standard network and vendor library exceptions into localized domain-specific exceptions, preventing abrupt crash dumps:

- **`ConfigError`**: Raised if environment variables are missing, empty, or contain default placeholder strings.
- **`ValidationError`**: Raised when local validations fail (e.g. quantity is negative, or a price is supplied for market orders). It blocks invalid network requests to Binance.
- **`BinanceAPIError`**: Catches errors from the Binance servers (such as insufficient margin, invalid API credentials, or exceeding position limits) and prints the API error code, HTTP status, and specific reason messages.
- **`NetworkError`**: Raised in case of timeout or connection drops.

All CLI exceptions are styled with `typer.secho` in colored outputs and return standard non-zero exit codes (`sys.exit(1)`).

---

## Design Decisions, Assumptions & Future Improvements

### Design Decisions
* **Type Safety & Models**: We avoid using generic dictionaries or tuples for passing responses. The model classes in `bot/models.py` guarantee that fields are typed and normalized.
* **Separation of Concerns**: Validations are fully independent of client implementations. We can run validations offline without initiating API connections.
* **Strict Fail-Fast**: If validation fails locally, the CLI exits immediately. Invalid requests never reach the external server, conserving rate limits and avoiding account bans.
* **Interactive loop**: Using interactive inputs with verification during loop prompts avoids requiring users to start the command over for typos.

### Assumptions
* The bot is designed strictly for USDT-M Futures on Testnet. Therefore, default URL endpoints point specifically to `testnet.binancefuture.com`.
* In futures contracts, placing limit orders requires specifying `timeInForce`. We assume `GTC` (Good 'Til Cancelled) as the standard behavior, which is hardcoded inside the client.

### Future Improvements
* **Support for Stop-Loss and Take-Profit**: Add support for trigger orders (`STOP_MARKET`, `TAKE_PROFIT_MARKET`).
* **Multi-Asset Validation**: Currently, symbols are validated for format (alphanumeric). Fetching active symbol attributes from `futures_exchange_info()` would enable checking symbol existence and checking step-size, tick-size, and minimum quantity requirements dynamically.
* **Async IO Support**: Upgrading the client to `AsyncClient` from `python-binance` for ultra-low latency executions.

---

## Screenshots Section Placeholders

### 1. Direct Order Placement (CLI)
```
[Insert Screenshot of standard cli execution with green successful order receipt]
```

### 2. Interactive Guide Wizard (CLI)
```
[Insert Screenshot of interactive loop showing verification steps and confirmation]
```

### 3. Log File Output
```
[Insert Screenshot of log file logs/trading_bot.log showing timestamped entries]
```

---

## License

This project is licensed under the MIT License - see the LICENSE details.
#   b i n a n c e - f u t u r e s - t r a d i n g - b o t  
 