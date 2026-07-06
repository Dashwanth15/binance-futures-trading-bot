# Binance Futures Trading Bot

A production-grade Python Command Line Interface (CLI) application for placing Market and Limit orders on the Binance USDT-M Futures Testnet. Built with a focus on modularity, input validation, and structured error handling.

---

## Project Overview

This trading bot provides a clean terminal interface to interact with the Binance Futures Testnet API. Developed as a hiring assignment, it demonstrates backend software engineering best practices including layered architecture, defensive parameter checks, and rotating file logging.

---

## Features

* **USDT-M Futures Testnet**: Fully configured to execute orders on the Binance Testnet environment.
* **Order Support**: Supports Market and Limit orders for both BUY and SELL directions.
* **Layered Architecture**: Strictly separates the interface, validation, business logic, and API client layers.
* **Defensive Local Validation**: Validates inputs locally to prevent invalid requests from reaching the API.
* **Interactive Mode**: Guided console wizard with dynamic connection and credential pre-checks.
* **Structured Logging**: Automatic size-based rotating file logs to control disk space consumption.
* **Robust Exception Wrapping**: Converts API, configuration, and network failures into user-friendly output.

---

## Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python** | Primary development language. |
| **python-binance** | Integration with the Binance Futures API. |
| **Typer** | CLI builder based on standard Python type hints. |
| **python-dotenv** | Environment configuration management. |
| **logging (Rotating)** | Dynamic log tracking with automatic size limits. |

---

## Project Structure

```
binance-futures-trading-bot/
├── bot/
│   ├── __init__.py           # Package initialization.
│   ├── client.py             # Communication client wrapper for Binance.
│   ├── config.py             # Configuration loader and validator.
│   ├── exceptions.py         # Custom domain exceptions hierarchy.
│   ├── logging_config.py     # Log rotation and handler configurations.
│   ├── models.py             # Request and response data structures.
│   ├── orders.py             # Business logic execution processor.
│   └── validators.py         # Local parameter validation constraints.
├── logs/
│   └── trading_bot.log       # Dynamic rotating logs database.
├── tests/
│   ├── __init__.py           # Unit tests package initialization.
│   └── test_validators.py    # Validators verification suite.
├── cli.py                    # Main CLI entrypoint.
├── .env.example              # Environment variables template.
├── .gitignore                # Git paths ignore rules.
├── README.md                 # Project documentation.
└── requirements.txt          # Third-party dependencies registry.
```

---

## Architecture

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

This layered design decouples interface inputs from API network operations. Validations and configs are isolated, allowing easy client replacements or business rules scaling without breaking the CLI.

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dashwanth15/binance-futures-trading-bot.git
   cd binance-futures-trading-bot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the environment**:
   * **Windows (PowerShell)**: `.venv\Scripts\Activate.ps1`
   * **Windows (CMD)**: `.venv\Scripts\activate.bat`
   * **macOS/Linux**: `source .venv/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Environment Variables

Copy the `.env.example` template into `.env`:
```bash
cp .env.example .env
```

Configure your credentials in `.env`:
```env
BINANCE_API_KEY=your_binance_testnet_api_key
BINANCE_SECRET_KEY=your_binance_testnet_secret_key
BINANCE_USE_TESTNET=True
```

* `BINANCE_API_KEY`: API Key generated from the Binance Futures Testnet.
* `BINANCE_SECRET_KEY`: Secret Key generated from the Binance Futures Testnet.
* `BINANCE_USE_TESTNET`: Directs communication to the Testnet environment when set to True.

---

## Usage

### 1. Market BUY
```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### 2. Market SELL
```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### 3. Limit BUY
```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 55000.0
```

### 4. Limit SELL
```bash
python cli.py place-order --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 68000.0
```

### 5. Interactive Mode
```bash
python cli.py interactive
```

---

## Logging

* **Location**: Logs are saved to `logs/trading_bot.log` and standard output.
* **Details**: Tracks incoming requests, local validations, vendor API response payloads, and exception traces.
* **Rotation**: Implements size-based log rotation (5MB per file, keeping 5 backup copies) to control disk usage.

---

## Error Handling

* **ConfigError**: Catches missing environment variables and default template values.
* **ValidationError**: Flags bad asset formats, invalid sides, and negative quantities locally.
* **BinanceAPIError**: Resolves Binance server errors (e.g. invalid keys or insufficient margin) safely.
* **NetworkError**: Captures socket timeouts and internet connection drops cleanly.

---

## Security

* **Secret Isolation**: Private keys are stored strictly in `.env` and loaded at runtime.
* **Repository Safety**: The `.env` configurations are ignored in `.gitignore` to prevent leakage.
* **Masking**: Omit keys and confidential transaction details from logs and stdout.

---

## Assumptions

* **USDT-M Futures Target**: Configured specifically for USDT-M Futures Testnet contracts.
* **Execution Parameters**: Limit orders default to `GTC` (Good 'Til Cancelled) time-in-force settings.
* **Default Settings**: Leverages default Testnet account tier settings for margin and symbol leverage.

---

## Future Improvements

* Support trigger-based order types (Stop-Limit, Take-Profit).
* Read dynamic symbol properties (min step sizes and quantity steps) via exchange info.
* Transition core codebase to AsyncIO for high-performance trades.
* Implement position monitoring commands to track active margins and PnL.
* Containerize the trading application with Docker.
* Create a lightweight test suite verifying API connectivity.

---

## Proof of Implementation

Proof of successful execution, parameter validation, and connection testing has been provided separately as a PDF document containing terminal execution logs and verification evidence.

---

## Conclusion

This Binance Futures Trading Bot demonstrates best practices in Python development: a clean decoupled architecture, robust error boundaries, rotating logs, and user interfaces. The code is modular, type-hinted, and ready for deployment.