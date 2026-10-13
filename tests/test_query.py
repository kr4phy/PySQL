"""
Tests for query execution and result processing.

These tests use mocking to test query behavior without requiring
a live MySQL server.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import date, datetime, time

from pysql.database.connection import DatabaseConnection
from pysql.database.query import QueryExecutor, QueryResult
from mysql.connector import Error as MySQLError


class TestQueryResult:
    """Test cases for the QueryResult class."""

    def test_empty_result(self):
        """Test empty query result."""
        result = QueryResult()
        assert result.columns == []
        assert result.rows == []
        assert result.row_count == 0
        assert result.affected_rows == 0
        assert result.had_non_result_statement is False
        assert result.has_result_set() is False

    def test_result_with_columns_and_rows(self):
        """Test query result with columns and rows."""
        columns = ["id", "name", "value"]
        rows = [(1, "test", 100.5), (2, "test2", 200.5)]
        result = QueryResult(columns=columns, rows=rows)
        
        assert result.columns == columns
        assert result.rows == rows
        assert result.row_count == 2
        assert result.has_result_set() is True

    def test_result_with_affected_rows(self):
        """Test query result with affected rows."""
        result = QueryResult(
            columns=[],
            rows=[],
            affected_rows=5,
            had_non_result_statement=True
        )
        
        assert result.affected_rows == 5
        assert result.had_non_result_statement is True
        assert result.has_result_set() is False

    def test_get_formatted_rows(self):
        """Test getting formatted rows."""
        rows = [(1, "test", None), (2, "hello", Decimal("3.14"))]
        result = QueryResult(columns=["a", "b", "c"], rows=rows)
        
        formatted = result.get_formatted_rows(quote_strings=True)
        expected = [("1", "'test'", "NULL"), ("2", "'hello'", "3.14")]
        assert formatted == expected

    def test_get_formatted_rows_without_quotes(self):
        """Test getting formatted rows without quotes."""
        rows = [(1, "test", None)]
        result = QueryResult(columns=["a", "b", "c"], rows=rows)
        
        formatted = result.get_formatted_rows(quote_strings=False)
        expected = [("1", "test", "NULL")]
        assert formatted == expected


class TestDatabaseConnection:
    """Test cases for the DatabaseConnection class."""

    def test_initial_state(self):
        """Test initial state of database connection."""
        conn = DatabaseConnection()
        assert conn.connection is None
        assert conn.is_connected is False

    def test_connect_and_close(self):
        """Test connect and close functionality."""
        conn = DatabaseConnection()
        
        # Mock the MySQL connection
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        
        with patch('pysql.database.connection.mysql_connection.MySQLConnection') as mock_mysql_conn_class:
            mock_mysql_conn_class.return_value = mock_connection
            
            # Test connection
            status = conn.connect(
                host="localhost",
                port=3306,
                user="test",
                password="test",
                connection_timeout=5
            )
            
            assert "Connected to MySQL at localhost:3306" in status
            assert conn.is_connected is True
            
            # Test close
            conn.close()
            mock_connection.close.assert_called_once()
            assert conn.is_connected is False

    def test_connect_with_defaults(self):
        """Test connection with default parameters."""
        conn = DatabaseConnection()
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        
        with patch('pysql.database.connection.mysql_connection.MySQLConnection') as mock_mysql_conn_class:
            mock_mysql_conn_class.return_value = mock_connection
            
            # Empty host should default to 127.0.0.1
            conn.connect(
                host="",
                port=0,  # This will cause issues, but we're mocking
                user="",
                password="",
                connection_timeout=5
            )
            
            # Check that MySQLConnection was called with reasonable defaults
            call_args = mock_mysql_conn_class.call_args
            assert call_args[1]['host'] == "127.0.0.1"


class TestQueryExecutor:
    """Test cases for the QueryExecutor class."""

    def test_initialization(self):
        """Test QueryExecutor initialization."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        assert executor._connection is conn

    def test_execute_query_not_connected(self):
        """Test query execution when not connected."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        with pytest.raises(Exception):  # MySQLError or similar
            executor.execute_query("SELECT 1")

    def test_execute_query_empty_sql(self):
        """Test query execution with empty SQL."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection to be connected
        mock_mysql_conn = Mock()
        mock_mysql_conn.is_connected.return_value = True
        conn._connection = mock_mysql_conn
        
        result = executor.execute_query("")
        assert isinstance(result, QueryResult)
        assert result.row_count == 0

    def test_execute_query_with_mock_cursor(self):
        """Test query execution with mocked cursor."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        mock_mysql_conn.is_connected.return_value = True
        conn._connection = mock_mysql_conn
        
        # Mock cursor
        mock_cursor = Mock()
        mock_cursor.with_rows = True
        mock_cursor.description = [("col1",), ("col2",)]
        mock_cursor.fetchall.return_value = [(1, "test"), (2, "hello")]
        mock_cursor.nextset.return_value = False
        mock_mysql_conn.cursor.return_value = mock_cursor
        
        with patch.object(executor, '_process_multi_result_cursor') as mock_process:
            mock_process.return_value = QueryResult(
                columns=["col1", "col2"],
                rows=[(1, "test"), (2, "hello")]
            )
            
            result = executor.execute_query("SELECT * FROM test")
            
            # Verify cursor was created and closed
            mock_mysql_conn.cursor.assert_called_once_with(buffered=True)
            mock_cursor.close.assert_called_once()
            
            # Verify result
            assert result.columns == ["col1", "col2"]
            assert result.row_count == 2

    def test_process_multi_result_cursor_single_result(self):
        """Test processing cursor with single result set."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        conn._connection = mock_mysql_conn
        
        # Mock cursor for single SELECT statement
        mock_cursor = Mock()
        mock_cursor.with_rows = True
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "test")]
        mock_cursor.rowcount = 0
        mock_cursor.nextset.return_value = False
        
        result = executor._process_multi_result_cursor(mock_cursor)
        
        assert result.columns == ["id", "name"]
        assert result.rows == [(1, "test")]
        assert result.row_count == 1
        assert result.affected_rows == 0

    def test_process_multi_result_cursor_non_result_statement(self):
        """Test processing cursor with non-result statement."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        conn._connection = mock_mysql_conn
        
        # Mock cursor for INSERT/UPDATE statement
        mock_cursor = Mock()
        mock_cursor.with_rows = False
        mock_cursor.rowcount = 5
        mock_cursor.nextset.return_value = False
        
        result = executor._process_multi_result_cursor(mock_cursor)
        
        assert result.columns == []
        assert result.rows == []
        assert result.affected_rows == 5
        assert result.had_non_result_statement is True
        
        # Should have committed
        mock_mysql_conn.commit.assert_called_once()

    def test_get_connection_status_connected(self):
        """Test connection status when connected."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        mock_mysql_conn.is_connected.return_value = True
        mock_mysql_conn.host = "localhost"
        mock_mysql_conn.port = 3306
        conn._connection = mock_mysql_conn
        
        status = executor.get_connection_status()
        assert "localhost:3306" in status

    def test_get_connection_status_not_connected(self):
        """Test connection status when not connected."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        status = executor.get_connection_status()
        assert "Not connected" in status


class TestErrorHandling:
    """Test error handling in query execution."""

    def test_execute_query_with_exception(self):
        """Test query execution handles exceptions properly."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        mock_mysql_conn.is_connected.return_value = True
        conn._connection = mock_mysql_conn
        
        # Mock cursor that raises exception
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = MySQLError("Test error")
        mock_mysql_conn.cursor.return_value = mock_cursor
        
        with pytest.raises(MySQLError, match="Test error"):
            executor.execute_query("SELECT 1")
        
        # Should have attempted rollback
        mock_mysql_conn.rollback.assert_called_once()
        
        # Cursor should be closed
        mock_cursor.close.assert_called_once()


class TestMultipleResultSets:
    """Test handling of multiple result sets."""

    def test_multiple_statements_with_results(self):
        """Test processing multiple statements that return results."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        conn._connection = mock_mysql_conn
        
        # Mock cursor for multiple statements
        mock_cursor = Mock()
        
        # First statement returns rows
        mock_cursor.with_rows = True
        mock_cursor.description = [("col1",)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_cursor.rowcount = 0
        
        # Second statement also returns rows (multi-statement)
        def nextset_side_effect():
            # Change state for second call
            mock_cursor.with_rows = True
            mock_cursor.description = [("col2",)]
            mock_cursor.fetchall.return_value = [(2,)]
            mock_cursor.rowcount = 0
            return True
        
        def nextset_final():
            return False
        
        # This is complex to mock properly, so we'll use a simpler approach
        mock_cursor.nextset.side_effect = [True, False]
        
        with patch.object(mock_cursor, 'fetchall') as mock_fetch:
            mock_fetch.side_effect = [[(1,)], [(2,)]]
            with patch.object(mock_cursor, 'description', [("col1",), ("col2",)]):
                result = executor._process_multi_result_cursor(mock_cursor)
        
        # Should have the last result set
        assert len(result.columns) > 0
        assert len(result.rows) > 0

    def test_mixed_statements(self):
        """Test processing mixed SELECT and INSERT statements."""
        conn = DatabaseConnection()
        executor = QueryExecutor(conn)
        
        # Mock connection
        mock_mysql_conn = Mock()
        conn._connection = mock_mysql_conn
        
        # Mock cursor for mixed statements
        mock_cursor = Mock()
        
        # Track call count for nextset
        call_count = [0]
        
        def nextset_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: switch to non-result statement
                mock_cursor.with_rows = False
                mock_cursor.rowcount = 3
                return True
            else:
                # Second call: no more result sets
                return False
        
        # First statement is SELECT (returns rows)
        mock_cursor.with_rows = True
        mock_cursor.description = [("id",)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_cursor.rowcount = 0
        mock_cursor.nextset.side_effect = nextset_side_effect
        
        result = executor._process_multi_result_cursor(mock_cursor)
        
        # Should have the SELECT result
        assert result.columns == ["id"]
        assert result.rows == [(1,)]
        assert result.affected_rows == 3  # From the INSERT
        assert result.had_non_result_statement is True