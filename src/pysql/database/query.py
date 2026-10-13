"""
SQL query execution and result processing for PySQL.

This module handles SQL execution, cursor lifecycle, result-set processing,
and transaction handling.
"""

from typing import Optional, Any, List, Tuple, Union, Iterator
from mysql.connector import cursor as mysql_cursor
from mysql.connector import connection as mysql_connection
from mysql.connector import Error as MySQLError
from .connection import DatabaseConnection
from pysql.services.formatter import format_row


class QueryResult:
    """
    Represents the result of a SQL query execution.
    
    Attributes:
        columns: List of column names for the result set
        rows: List of row tuples containing the data
        row_count: Number of rows in the result set
        affected_rows: Number of rows affected by non-query statements
        had_non_result_statement: Whether any statement was not a SELECT/result-returning statement
    """
    
    def __init__(
        self,
        columns: Optional[List[str]] = None,
        rows: Optional[List[tuple]] = None,
        affected_rows: int = 0,
        had_non_result_statement: bool = False
    ):
        self.columns = columns or []
        self.rows = rows or []
        self.row_count = len(rows) if rows else 0
        self.affected_rows = affected_rows
        self.had_non_result_statement = had_non_result_statement
    
    def has_result_set(self) -> bool:
        """Check if this result contains a result set (rows with columns)."""
        return len(self.columns) > 0 and self.row_count > 0
    
    def get_formatted_rows(self, quote_strings: bool = True) -> List[Tuple[str, ...]]:
        """Get all rows formatted for display."""
        if self.rows:
            return [format_row(row, quote_strings) for row in self.rows]
        return []


class QueryExecutor:
    """
    Executes SQL queries and manages cursor lifecycle.
    
    This class provides explicit interfaces for SQL execution with proper
    cursor cleanup and transaction management.
    """
    
    def __init__(self, connection: DatabaseConnection):
        """
        Initialize the query executor with a database connection.
        
        Args:
            connection: DatabaseConnection instance for executing queries
        """
        self._connection = connection
    
    def execute_query(
        self, 
        sql: str, 
        quote_strings: bool = True
    ) -> QueryResult:
        """
        Execute a SQL query and return the result.
        
        This method handles:
        - Creating and managing cursor lifecycle
        - Processing multiple statements and result sets
        - Tracking affected rows
        - Transaction handling (commit/rollback)
        - Proper cleanup in case of errors
        
        Args:
            sql: SQL query string to execute
            quote_strings: Whether to apply SQL-literal-style formatting to strings
        
        Returns:
            QueryResult object containing columns, rows, and metadata
        
        Raises:
            MySQLError: If query execution fails
        """
        if not self._connection.is_connected:
            raise MySQLError("Not connected to database")
        
        if not sql or not sql.strip():
            return QueryResult()
        
        cursor = None
        try:
            # Use buffered cursor to support multi-statement execution
            # and to consume result sets properly
            cursor = self._connection.connection.cursor(buffered=True)
            cursor.execute(sql, map_results=True)
            
            return self._process_multi_result_cursor(cursor, quote_strings)
            
        except MySQLError as exc:
            # Rollback on error
            try:
                if self._connection.is_connected:
                    self._connection.connection.rollback()
            except Exception:
                # Silently ignore rollback errors
                pass
            raise exc
        finally:
            # Always close cursor
            if cursor is not None:
                try:
                    cursor.close()
                except Exception:
                    # Silently ignore cursor close errors
                    pass
    
    def _process_multi_result_cursor(
        self, 
        cursor: mysql_cursor.MySQLCursor, 
        quote_strings: bool = True
    ) -> QueryResult:
        """
        Process a cursor that may contain multiple result sets.
        
        This method handles:
        - Multiple statements that may return multiple result sets
        - Non-result-returning statements (INSERT, UPDATE, DELETE, etc.)
        - Proper consumption of all result sets using cursor.nextset()
        - Tracking affected rows accurately
        
        Args:
            cursor: Buffered MySQL cursor with executed query
            quote_strings: Whether to format string values
        
        Returns:
            QueryResult object containing the last result set and metadata
        """
        last_columns: Optional[List[str]] = None
        last_rows: Optional[List[tuple]] = None
        total_affected = 0
        had_non_result_statement = False
        
        while True:
            if cursor.with_rows:
                # This statement returned rows (SELECT, SHOW, etc.)
                rows = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                # Show the last statement that returned rows
                last_columns, last_rows = columns, rows
            else:
                # This was a non-result-returning statement (INSERT, UPDATE, DELETE, etc.)
                had_non_result_statement = True
                if cursor.rowcount > 0:
                    total_affected += cursor.rowcount
            
            # Important: advance through and consume every result set
            if not cursor.nextset():
                break
        
        # Commit if we had non-result statements that might have modified data
        if had_non_result_statement:
            try:
                self._connection.connection.commit()
            except Exception:
                # Silently ignore commit errors
                pass
        
        if last_columns is not None and last_rows is not None:
            return QueryResult(
                columns=last_columns,
                rows=last_rows,
                affected_rows=total_affected,
                had_non_result_statement=had_non_result_statement
            )
        else:
            return QueryResult(
                columns=[],
                rows=[],
                affected_rows=total_affected,
                had_non_result_statement=had_non_result_statement
            )
    
    def get_connection_status(self) -> str:
        """Get a status message about the current connection."""
        if self._connection.is_connected:
            conn = self._connection.connection
            return f"Connected to MySQL at {conn.host}:{conn.port}"
        return "Not connected. Connect to a MySQL server to run queries."
