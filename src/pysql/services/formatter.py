"""
Database value formatting service for PySQL.

This module provides functionality to format database values for display,
with support for SQL-literal-style formatting.
"""

from decimal import Decimal
from datetime import date, datetime, time
from typing import Any, Union


def display_value(value: Any, quote_strings: bool = True) -> str:
    """
    Format a returned database value for display.
    
    Args:
        value: The database value to format.
        quote_strings: If True, strings and temporal values are quoted 
                      in SQL-literal style (with embedded single quotes doubled).
    
    Returns:
        Formatted string representation of the value.
    
    The formatting rules are:
    - None is displayed as "NULL"
    - Strings are enclosed in single quotes when quote_strings is True
    - Embedded single quotes are escaped by doubling them
    - date, datetime, and time values are formatted using ISO representations
      and quoted when quote_strings is True
    - Decimal values retain their string representation
    - Other values are converted to strings
    
    Note: Disabling quote formatting changes presentation only; it does not 
    modify actual database values.
    """
    if value is None:
        return "NULL"
    
    if isinstance(value, str):
        if quote_strings:
            # SQL-style escaping: embedded single quotes are doubled.
            return "'" + value.replace("'", "''") + "'"
        return value
    
    if isinstance(value, (date, datetime, time)):
        if isinstance(value, datetime):
            text = value.isoformat(sep=" ")
        else:
            text = value.isoformat()
        if quote_strings:
            return "'" + text.replace("'", "''") + "'"
        return text
    
    if isinstance(value, Decimal):
        return str(value)
    
    return str(value)


def format_row(row: tuple, quote_strings: bool = True) -> tuple[str, ...]:
    """
    Format all values in a database row for display.
    
    Args:
        row: A tuple of database values (typically from cursor.fetchone() or cursor.fetchall())
        quote_strings: If True, apply SQL-literal-style formatting to strings
    
    Returns:
        Tuple of formatted string values.
    """
    return tuple(display_value(value, quote_strings) for value in row)
