"""
Tests for the display_value formatter functionality.

These tests cover all documented display_value() formatting cases.
"""

import pytest
from decimal import Decimal
from datetime import date, datetime, time

from pysql.services.formatter import display_value, format_row


class TestDisplayValue:
    """Test cases for the display_value function."""

    def test_none_value(self):
        """Test that None is displayed as 'NULL'."""
        assert display_value(None) == "NULL"
        assert display_value(None, quote_strings=True) == "NULL"
        assert display_value(None, quote_strings=False) == "NULL"

    def test_string_with_quote_formatting(self):
        """Test string formatting with quote formatting enabled."""
        assert display_value("hello") == "'hello'"
        assert display_value("hello", quote_strings=True) == "'hello'"

    def test_string_without_quote_formatting(self):
        """Test string formatting with quote formatting disabled."""
        assert display_value("hello", quote_strings=False) == "hello"

    def test_string_with_embedded_single_quotes(self):
        """Test string with embedded single quotes are escaped by doubling."""
        result = display_value("it's", quote_strings=True)
        assert result == "'it''s'"
        
        result = display_value("it's a test", quote_strings=True)
        assert result == "'it''s a test'"
        
        result = display_value("it's", quote_strings=False)
        assert result == "it's"

    def test_string_with_multiple_embedded_quotes(self):
        """Test string with multiple embedded single quotes."""
        result = display_value("it's a 'test' case", quote_strings=True)
        assert result == "'it''s a ''test'' case'"

    def test_date_formatting(self):
        """Test date formatting."""
        test_date = date(2023, 12, 25)
        
        # With quote formatting
        result = display_value(test_date, quote_strings=True)
        assert result == "'2023-12-25'"
        
        # Without quote formatting
        result = display_value(test_date, quote_strings=False)
        assert result == "2023-12-25"

    def test_datetime_formatting(self):
        """Test datetime formatting."""
        test_datetime = datetime(2023, 12, 25, 14, 30, 45)
        
        # With quote formatting
        result = display_value(test_datetime, quote_strings=True)
        assert result == "'2023-12-25 14:30:45'"
        
        # Without quote formatting
        result = display_value(test_datetime, quote_strings=False)
        assert result == "2023-12-25 14:30:45"

    def test_time_formatting(self):
        """Test time formatting."""
        test_time = time(14, 30, 45)
        
        # With quote formatting
        result = display_value(test_time, quote_strings=True)
        assert result == "'14:30:45'"
        
        # Without quote formatting
        result = display_value(test_time, quote_strings=False)
        assert result == "14:30:45"

    def test_decimal_formatting(self):
        """Test Decimal formatting."""
        test_decimal = Decimal("123.456")
        
        result = display_value(test_decimal, quote_strings=True)
        assert result == "123.456"
        
        result = display_value(test_decimal, quote_strings=False)
        assert result == "123.456"

    def test_decimal_with_context(self):
        """Test Decimal with different precision."""
        # Test very precise decimal - may use scientific notation
        test_decimal = Decimal("0.0000001")
        result = display_value(test_decimal)
        # Decimal can be displayed as scientific notation or decimal
        assert result in ["0.0000001", "1E-7"]
        
        # Test large decimal
        test_decimal = Decimal("999999999999.99")
        result = display_value(test_decimal)
        assert result in ["999999999999.99", "9.99999999999999E+11"]

    def test_integer_formatting(self):
        """Test integer formatting."""
        assert display_value(42) == "42"
        assert display_value(0) == "0"
        assert display_value(-100) == "-100"

    def test_float_formatting(self):
        """Test float formatting."""
        assert display_value(3.14) == "3.14"
        assert display_value(-2.718) == "-2.718"

    def test_boolean_formatting(self):
        """Test boolean formatting."""
        assert display_value(True) == "True"
        assert display_value(False) == "False"

    def test_empty_string(self):
        """Test empty string formatting."""
        assert display_value("") == "''"
        assert display_value("", quote_strings=True) == "''"
        assert display_value("", quote_strings=False) == ""

    def test_whitespace_string(self):
        """Test whitespace string formatting."""
        assert display_value(" ") == "' '"
        assert display_value("\t") == "'\t'"  # Note: tab is preserved as is
        assert display_value("\n") == "'\n'"  # Note: newline is preserved as is


class TestFormatRow:
    """Test cases for the format_row function."""

    def test_empty_row(self):
        """Test formatting an empty row."""
        result = format_row(())
        assert result == ()

    def test_single_value_row(self):
        """Test formatting a row with a single value."""
        result = format_row(("test",))
        assert result == ("'test'",)

    def test_mixed_types_row(self):
        """Test formatting a row with mixed types."""
        row = (1, "hello", None, Decimal("3.14"), date(2023, 1, 1))
        result = format_row(row)
        expected = ("1", "'hello'", "NULL", "3.14", "'2023-01-01'")
        assert result == expected

    def test_row_without_quotes(self):
        """Test formatting a row without quote formatting."""
        row = (1, "hello", None)
        result = format_row(row, quote_strings=False)
        expected = ("1", "hello", "NULL")
        assert result == expected

    def test_row_with_embedded_quotes(self):
        """Test formatting a row with embedded quotes."""
        row = ("it's", "test's value")
        result = format_row(row)
        expected = ("'it''s'", "'test''s value'")
        assert result == expected