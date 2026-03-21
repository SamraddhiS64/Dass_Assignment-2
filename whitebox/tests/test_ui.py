# whitebox/tests/test_ui.py

import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../moneypoly'))

from moneypoly import ui


class TestSafeIntInput:

    def test_valid_integer_returns_int(self):
        """
        user types a valid integer.
        int(input()) succeeds, returns the number.
        """
        with patch("builtins.input", return_value="5"):
            result = ui.safe_int_input("Enter: ")
        assert result == 5

    def test_invalid_string_returns_default(self):
        """
        user types letters, raises ValueError.
        except block returns default value.
        """
        with patch("builtins.input", return_value="abc"):
            result = ui.safe_int_input("Enter: ", default=0)
        assert result == 0

    def test_empty_input_returns_default(self):
        """
        Edge case, user presses Enter with nothing typed.
        int("") raises ValueError, returns default.
        """
        with patch("builtins.input", return_value=""):
            result = ui.safe_int_input("Enter: ", default=99)
        assert result == 99

    def test_negative_integer(self):
        """
        Edge case, negative numbers are valid integers.
        """
        with patch("builtins.input", return_value="-10"):
            result = ui.safe_int_input("Enter: ")
        assert result == -10

    def test_zero(self):
        """
        Edge case, zero is a valid integer.
        """
        with patch("builtins.input", return_value="0"):
            result = ui.safe_int_input("Enter: ")
        assert result == 0

    def test_float_string_returns_default(self):
        """
        Edge case, "3.5" is not an int, raises ValueError.
        Returns default.
        """
        with patch("builtins.input", return_value="3.5"):
            result = ui.safe_int_input("Enter: ", default=0)
        assert result == 0

    def test_symbols_return_default(self):
        """
        Edge case, symbols like $ raise ValueError.
        Returns default.
        """
        with patch("builtins.input", return_value="$100"):
            result = ui.safe_int_input("Enter: ", default=0)
        assert result == 0

    def test_large_integer_valid(self):
        """
        Edge case, very large integer still parsed correctly.
        """
        with patch("builtins.input", return_value="999999"):
            result = ui.safe_int_input("Enter: ")
        assert result == 999999


class TestConfirm:

    def test_y_returns_true(self):
        """
        user types 'y', returns True.
        """
        with patch("builtins.input", return_value="y"):
            result = ui.confirm("Continue? ")
        assert result is True

    def test_n_returns_false(self):
        """
        user types 'n', returns False.
        """
        with patch("builtins.input", return_value="n"):
            result = ui.confirm("Continue? ")
        assert result is False

    def test_uppercase_y_returns_true(self):
        """
        'Y' should also return True after .lower().
        """
        with patch("builtins.input", return_value="Y"):
            result = ui.confirm("Continue? ")
        assert result is True

    def test_uppercase_n_returns_false(self):
        """
        'N' returns False.
        """
        with patch("builtins.input", return_value="N"):
            result = ui.confirm("Continue? ")
        assert result is False

    def test_empty_input_returns_false(self):
        """
        empty input is not 'y', returns False.
        """
        with patch("builtins.input", return_value=""):
            result = ui.confirm("Continue? ")
        assert result is False

    def test_random_word_returns_false(self):
        """
        anything other than 'y' returns False.
        """
        with patch("builtins.input", return_value="yes"):
            result = ui.confirm("Continue? ")
        assert result is False

    def test_spaces_stripped_y_returns_true(self):
        """
        '  y  ' with spaces — strip() removes them.
        Returns True.
        """
        with patch("builtins.input", return_value="  y  "):
            result = ui.confirm("Continue? ")
        assert result is True

    def test_spaces_stripped_n_returns_false(self):
        """
        '  n  ' with spaces stripped returns False.
        """
        with patch("builtins.input", return_value="  n  "):
            result = ui.confirm("Continue? ")
        assert result is False


class TestFormatCurrency:

    def test_formats_basic_amount(self):
        """$1500 formatted correctly."""
        assert ui.format_currency(1500) == "$1,500"

    def test_formats_zero(self):
        """zero formats correctly."""
        assert ui.format_currency(0) == "$0"

    def test_formats_large_amount(self):
        """large number has correct comma separators."""
        assert ui.format_currency(1000000) == "$1,000,000"

    def test_formats_small_amount(self):
        """small amount under 1000."""
        assert ui.format_currency(50) == "$50"