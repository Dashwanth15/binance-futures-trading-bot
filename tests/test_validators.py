"""
Unit tests for the validator functions in bot/validators.py.
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path so 'bot' package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_order_params,
)
from bot.exceptions import ValidationError


class TestValidators(unittest.TestCase):
    """Test suite for bot validators."""

    def test_validate_symbol_success(self) -> None:
        """Verify symbol normalization and format check succeeds for valid patterns."""
        self.assertEqual(validate_symbol("BTCUSDT"), "BTCUSDT")
        self.assertEqual(validate_symbol("ethusdt"), "ETHUSDT")
        self.assertEqual(validate_symbol("  solusdt  "), "SOLUSDT")

    def test_validate_symbol_failures(self) -> None:
        """Verify invalid symbols raise ValidationError."""
        invalid_symbols = ["", "  ", "BT-USDT", "BTC/USDT", 12345, "A" * 16, "BT"]
        for sym in invalid_symbols:
            with self.assertRaises(ValidationError):
                validate_symbol(sym)  # type: ignore

    def test_validate_side_success(self) -> None:
        """Verify side normalization and format check succeeds for valid directions."""
        self.assertEqual(validate_side("BUY"), "BUY")
        self.assertEqual(validate_side("sell"), "SELL")
        self.assertEqual(validate_side("  buy  "), "BUY")

    def test_validate_side_failures(self) -> None:
        """Verify invalid sides raise ValidationError."""
        invalid_sides = ["", "HOLD", "NONE", "buyy", 123]
        for side in invalid_sides:
            with self.assertRaises(ValidationError):
                validate_side(side)  # type: ignore

    def test_validate_order_type_success(self) -> None:
        """Verify order type validation and normalization."""
        self.assertEqual(validate_order_type("MARKET"), "MARKET")
        self.assertEqual(validate_order_type("limit"), "LIMIT")
        self.assertEqual(validate_order_type("  Market  "), "MARKET")

    def test_validate_order_type_failures(self) -> None:
        """Verify invalid order types raise ValidationError."""
        invalid_types = ["", "STOP_LOSS", "TAKE_PROFIT", 123]
        for t in invalid_types:
            with self.assertRaises(ValidationError):
                validate_order_type(t)  # type: ignore

    def test_validate_quantity_success(self) -> None:
        """Verify quantity checks convert and bounds check successfully."""
        self.assertEqual(validate_quantity(0.01), 0.01)
        self.assertEqual(validate_quantity("0.5"), 0.5)
        self.assertEqual(validate_quantity(10), 10.0)

    def test_validate_quantity_failures(self) -> None:
        """Verify invalid quantities raise ValidationError."""
        invalid_qtys = [0, -0.1, "abc", None]
        for qty in invalid_qtys:
            with self.assertRaises(ValidationError):
                validate_quantity(qty)  # type: ignore

    def test_validate_price_success(self) -> None:
        """Verify price requirements and validation based on order type."""
        # Limit order pricing
        self.assertEqual(validate_price("LIMIT", 60000), 60000.0)
        self.assertEqual(validate_price("LIMIT", "54320.10"), 54320.10)
        
        # Market order pricing
        self.assertIsNone(validate_price("MARKET", None))

    def test_validate_price_failures(self) -> None:
        """Verify invalid pricing bounds or unmatched order types fail."""
        # Limit order missing or negative pricing
        with self.assertRaises(ValidationError):
            validate_price("LIMIT", None)
        with self.assertRaises(ValidationError):
            validate_price("LIMIT", -10)
        with self.assertRaises(ValidationError):
            validate_price("LIMIT", "xyz")

        # Market order with price
        with self.assertRaises(ValidationError):
            validate_price("MARKET", 123)

    def test_validate_order_params_orchestration(self) -> None:
        """Verify validate_order_params orchestrates the checks."""
        res = validate_order_params("BTCUSDT", "BUY", "LIMIT", 0.01, 60000.0)
        self.assertEqual(res["symbol"], "BTCUSDT")
        self.assertEqual(res["side"], "BUY")
        self.assertEqual(res["type"], "LIMIT")
        self.assertEqual(res["quantity"], 0.01)
        self.assertEqual(res["price"], 60000.0)


if __name__ == "__main__":
    unittest.main()
