# Binance Futures Trading Bot

A production-grade Python CLI application for placing Market and Limit orders on the Binance USDT-M Futures Testnet. Designed as an engineering assessment, this project emphasizes separation of concerns, defensive validation, structured rotation logging, clean error handling, and robust security practices.

---

## Project Overview

The **Binance Futures Trading Bot** is a terminal-based interface designed to execute USDT-Margined futures contracts against the official Binance Futures Testnet API. The application communicates using the `python-binance` library and offers both standard command-line flags and a step-by-step interactive prompt wizard.

This application is built with a strict layered architecture, separating user interactions, validation logic, trading business rules, and API connection wrappers. It is designed to model a clean, scalable production application, avoiding tightly coupled structures and raw unhandled exceptions.

---

## Features

- [x] **Layered Architecture**: Decoupled interface, validation logic, business orchestrations, and API client wrapper layers.
- [x] **USDT-M Futures Testnet Integration**: Communicates directly with the Binance USDT-M Futures Testnet environment.
- [x] **Market Orders**: Placements of BUY and SELL market orders on futures symbols (e.g. BTCUSDT, ETHUSDT) based on quantity.
- [x] **Limit Orders**: Placements of BUY and SELL limit orders requiring specified target price values.
- [x] **Defensive Local Validation**: Strict validation checks parameters (formats, range bounds, requirements) offline, protecting against invalid network requests.
- [x] **Typer-based CLI**: Auto-documented commands with option descriptions and help flags.
- [x] **Interactive Mode**: Guided terminal setup that prompts for inputs, validates selections on-the-fly, and verifies connection.
- [x] **Structured Logging**: Automatic rotating log files with configurable rotation thresholds (5MB size, max 5 backup copies) to control disk usage.
- [x] **Graceful Error Handling**: Maps third-party network, config, and vendor API exceptions into human-friendly domain exceptions to avoid traceback stack dumps.
- [x] **Security Constraints**: Strict credential isolation via environment configurations, ensuring no secrets are printed, logged, or checked into source control.

---

## Project Architecture

This application employs a classic layered architecture where data and control flow downwards, and each layer has a single, well-defined responsibility.

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

### Responsibility Matrix:
- **CLI Layer (`cli.py`)**: Manages the interface, command arguments parsing, colors/formatting, confirmations, and the interactive wizard prompt.
- **Validation Layer (`bot/validators.py`)**: Performs defensive input checks locally. If validation fails, it raises custom errors, halting execution before contacting remote servers.
- **Business Logic Layer (`bot/orders.py`)**: Orchestrates incoming parameters, maps raw details into typed data models (`OrderRequest`), executes logic, and structures API output into normalized representations (`OrderResult`).
- **Binance Client Layer (`bot/client.py`)**: Authenticates via API keys, configures requests timeout parameters, communicates directly with endpoints, and wraps raw vendor exceptions into domain errors.

This architectural decoupling ensures the communication client can be modified, replaced, or mocked (e.g., during testing) without impacting validation logic, business processing, or user interfaces.

---

## Project Structure

```
binance-futures-trading-bot/
├── .vscode/
│   └── settings.json         # Workspace IDE Python path maps
├── bot/
│   ├── __init__.py           # Package initialization
│   ├── client.py             # Communication client wrapper around python-binance
│   ├── config.py             # Config loader validating environment secrets
│   ├── exceptions.py         # Custom application exception classes
│   ├── logging_config.py     # Setup for stream and rotating file logging
│   ├── models.py             # Structured request & response dataclasses
│   ├── orders.py             # Business logic order processors
│   └── validators.py         # Local parameter validation logic
├── logs/
│   ├── trading_bot.log       # Dynamic rotating logs file
│   ├── market_order.log      # Sample market order log snippet
│   └── limit_order.log       # Sample limit order log snippet
├── tests/
│   ├── __init__.py           # Unit tests package initialization
│   └── test_validators.py    # Unit tests suite for validators
├── cli.py                    # Application CLI entrypoint
├── .env.example              # Environment variables template
├── .gitignore                # Git paths ignore configurations
├── README.md                 # Project documentation
└── requirements.txt          # Third-party dependencies checklist
```

---

## Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python 3.11+** | The core programming language. |
| **python-binance** | Unofficial Python wrapper for the Binance Exchange API. |
| **Typer** | Library for building CLI applications based on Python type hints. |
| **python-dotenv** | Reads key-value pairs from `.env` files and sets them as environment variables. |
| **RotatingFileHandler** | Handles automatic daily log rotations to manage log file sizes. |
| **unittest** | Python standard library framework for code validation. |

---

## Prerequisites

- **Python 3.11+** installed on your system.
- A **Binance Futures Testnet** account. If you do not have one, you can register at [https://testnet.binancefuture.com](https://testnet.binancefuture.com).
- A pair of **Testnet API Key** and **Secret Key** generated from your testnet profile dashboard.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dashwanth15/binance-futures-trading-bot.git
   cd binance-futures-trading-bot
   ```

2. **Create a virtual environment** (recommended to isolate dependencies):
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **On Windows (PowerShell)**:
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   - **On Windows (CMD)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```
   - **On macOS/Linux**:
     ```bash
     source .venv/bin/activate
     ```

4. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

The application relies on environment variables to authenticate with the Binance Futures Testnet API. Copy the sample file `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure your `.env` file with your credentials:

```env
# Binance USDT-M Futures Testnet Credentials
BINANCE_API_KEY=your_binance_testnet_api_key_here
BINANCE_SECRET_KEY=your_binance_testnet_secret_key_here
BINANCE_USE_TESTNET=True
```

### Environment Parameters:
- `BINANCE_API_KEY`: The API key generated from the Binance Futures Testnet portal.
- `BINANCE_SECRET_KEY`: The Secret Key generated from the Binance Futures Testnet portal.
- `BINANCE_USE_TESTNET`: Configures endpoint targets. When set to `True` (default), the client targets `https://testnet.binancefuture.com`.

---

## Running the Application

Ensure your environment is configured before executing the commands.

### 1. Market BUY Order
Places a market order to buy a specific quantity of an asset:
```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 2. Market SELL Order
Places a market order to sell a specific quantity of an asset:
```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### 3. Limit BUY Order
Places a limit order to buy an asset at a specific price:
```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 55000.0
```

### 4. Limit SELL Order
Places a limit order to sell an asset at a specific price:
```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 68000.0
```

> [!NOTE]  
> Use the `--no-confirm` flag on any command to bypass the terminal safety prompt and submit orders immediately.

---

## Interactive CLI

For a guided terminal experience, launch the interactive wizard:

```bash
python cli.py interactive
```

### Interactive Benefits:
1. **Network Connectivity Test**: Pings the Binance Futures Testnet to verify connection status before prompting for credentials.
2. **Credential Pre-check**: Runs a lightweight account request to validate API keys before prompting for order inputs.
3. **Step-by-Step Validation**: Prompts for parameters sequentially, validating inputs on-the-fly and reporting errors immediately.
4. **Final Order Summary**: Displays a structured order summary and requires explicit confirmation before submitting the trade.

---

## Input Validation

The validation system in `bot/validators.py` prevents invalid requests from reaching the Binance API:

- **Symbol Check**: Verifies symbols match formatting rules (alphanumeric uppercase, 3-15 characters) using regex patterns (e.g. `BTCUSDT`).
- **Side Check**: Restricts inputs to `BUY` or `SELL`.
- **Type Check**: Restricts inputs to `MARKET` or `LIMIT`.
- **Quantity Bounds**: Ensures quantities are numeric and strictly greater than zero.
- **Price Constraints**: Enforces price presence and positive values for `LIMIT` orders, while validating that `MARKET` orders do not accept pricing parameters.

---

## Logging

Logging settings are configured in `bot/logging_config.py` using Python's standard `logging` library.

- **Storage**: Logs are written to both standard output and a file located at `logs/trading_bot.log`.
- **Rotation**: Employs `RotatingFileHandler` configured with a 5MB size limit and a maximum of 5 backup archives to prevent uncontrolled log file growth.
- **Structured Fields**: Logs include timestamps, log levels, originating modules, code locations (filename and line number), and message details.
- **Noise Control**: External network logging modules (`urllib3`, `requests`, and `websockets`) are muted to `WARNING` levels to ensure trace readability.
- **Log Events**: Captures application start, incoming requests, validations, API payloads, raw network responses, transaction successes, and failures.

---

## Error Handling

The application maps exceptions into custom exception classes, preventing traceback displays to the user:

- **`ConfigError`**: Raised when configurations are missing or default placeholders are detected.
- **`ValidationError`**: Raised when local parameter validation checks fail.
- **`BinanceAPIError`**: Wraps raw vendor communication exceptions (`BinanceAPIException`), capturing HTTP status codes, API error codes, and messages.
- **`NetworkError`**: Raised in case of request timeouts or connection failures.

All custom exceptions are styled and output with distinct terminal colors and non-zero exit codes (`sys.exit(1)`).

---

## Security

- **Environment Variable Isolation**: API credentials are loaded dynamically from `.env` at runtime.
- **Git Protection**: The local `.env` file is ignored in `.gitignore` to prevent committing secrets to repository hosting services.
- **Credential Masking**: Client logs and stdout messages omit API keys and secret strings.
- **No-Credential Warnings**: Config validators check if credentials match initial templates, prompting the user to configure their environment.

---

## Assumptions

- **Asset Focus**: The application is configured for USDT-M Futures on Testnet. Therefore, the connection wrapper points to `testnet.binancefuture.com`.
- **Order Execution Type**: Limit orders default to `GTC` (Good 'Til Cancelled) time-in-force parameters.
- **Leverage Rules**: Assumes default system account leverage settings on Testnet for executed symbols.

---

## Future Improvements

1. **Stop-Limit and Trigger Orders**: Add triggers for automated stop-loss, trailing stop, and take-profit executions.
2. **Dynamic Step-Size Check**: Integrate `futures_exchange_info()` to validate minimum quantities, step sizes, and price tick bounds dynamically.
3. **Async IO Support**: Rebuild components using `AsyncClient` from the `python-binance` package to support high-frequency, non-blocking executions.
4. **Position Monitoring**: Add CLI commands to monitor active positions, margin balances, and unrealized PnL.
5. **Docker Integration**: Package the application into a Docker container for isolated execution environments.

---

## Proof of Implementation

Proof of successful execution, parameter validation, and connection testing has been provided separately as a PDF document containing terminal execution logs and verification evidence.

---

## Conclusion

The **Binance Futures Trading Bot** is a clean, production-grade CLI application designed to interact with the Binance USDT-M Futures Testnet. Built with a modular layered architecture, it decouples validation, business logic, client communications, and command-line inputs. By incorporating strict offline validation, structured rotation logging, error mapping, and environment-based configuration, this project follows best practices for software engineering and maintainability.