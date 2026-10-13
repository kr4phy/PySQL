"""
Main application composition and startup for PySQL.

This module provides the main application class that composes all components
and handles the coordination between UI, database, and services.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Dict, Any
from mysql.connector import Error as MySQLError

from pysql.core.config import (
    APP_TITLE,
    STATUS_NOT_CONNECTED,
    STATUS_CONNECTION_FAILED,
    STATUS_QUERY_FAILED,
    CONNECTION_TIMEOUT
)
from pysql.database.connection import DatabaseConnection
from pysql.database.query import QueryExecutor, QueryResult
from pysql.ui.main_window import MainWindow


class PySQLApplication:
    """
    Main application class for PySQL.
    
    This class coordinates between the UI components, database connection,
    and query execution, maintaining proper separation of concerns.
    """
    
    def __init__(self):
        """Initialize the PySQL application."""
        # Initialize database connection
        self.database_connection = DatabaseConnection()
        
        # Initialize query executor with the database connection
        self.query_executor = QueryExecutor(self.database_connection)
        
        # Create main window with callbacks
        self.main_window = MainWindow(
            on_connect=self._handle_connect,
            on_execute_query=self._handle_execute_query,
            on_clear_results=self._handle_clear_results
        )
        
        # Track if we're connected to avoid redundant connection attempts
        self._is_connected = False
    
    def _handle_connect(self, connection_info: Dict[str, Any]) -> None:
        """
        Handle connection attempt from UI.
        
        Args:
            connection_info: Dictionary containing connection parameters
        """
        # Check if MySQL connector is available
        try:
            import mysql.connector
        except ImportError:
            self.main_window.show_error(
                "Missing dependency",
                "Install the MySQL connector first:\n\n"
                "python -m pip install mysql-connector-python"
            )
            return
        
        try:
            # Parse connection info
            host = connection_info.get("host", "127.0.0.1")
            port = int(connection_info.get("port", 3306))
            user = connection_info.get("user", "root")
            password = connection_info.get("password", "")
            database = connection_info.get("database", None)
            
            # Attempt connection
            status_message = self.database_connection.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connection_timeout=CONNECTION_TIMEOUT
            )
            
            self._is_connected = True
            self.main_window.update_status(status_message)
            self.main_window.show_info("Connected", "Successfully connected to MySQL.")
            
        except MySQLError as exc:
            self.database_connection.close()
            self._is_connected = False
            self.main_window.show_error("Connection failed", str(exc))
            self.main_window.update_status(STATUS_CONNECTION_FAILED)
        except ValueError:
            # Invalid port number
            self.main_window.show_error("Invalid port", "Port must be a valid integer.")
            self.main_window.update_status(STATUS_CONNECTION_FAILED)
        except Exception as exc:
            self.database_connection.close()
            self._is_connected = False
            self.main_window.show_error("Connection failed", str(exc))
            self.main_window.update_status(STATUS_CONNECTION_FAILED)
    
    def _handle_execute_query(
        self, 
        sql: str, 
        quote_strings: bool
    ) -> None:
        """
        Handle query execution request from UI.
        
        Args:
            sql: SQL query string to execute
            quote_strings: Whether to apply SQL-literal-style formatting
        """
        if not self._is_connected or not self.database_connection.is_connected:
            self.main_window.show_warning(
                "Not connected", 
                "Connect to a MySQL server first."
            )
            return
        
        if not sql:
            return
        
        try:
            # Execute query and get result
            result = self.query_executor.execute_query(sql, quote_strings)
            
            # Update UI based on result
            if result.has_result_set():
                formatted_rows = result.get_formatted_rows(quote_strings)
                self.main_window.display_results(result.columns, formatted_rows)
                self.main_window.update_status(f"{result.row_count} row(s) returned.")
            else:
                self.main_window.clear_results()
                if result.had_non_result_statement:
                    self.main_window.update_status(
                        f"Query completed. Rows affected: {result.affected_rows}. "
                        "Any pending changes were committed."
                    )
                else:
                    self.main_window.update_status("Query completed.")
                    
        except MySQLError as exc:
            # Error during query execution
            try:
                if self.database_connection.is_connected:
                    self.database_connection.connection.rollback()
            except Exception:
                pass
            self.main_window.show_error("Query failed", str(exc))
            self.main_window.update_status(STATUS_QUERY_FAILED)
        except Exception as exc:
            # Other errors
            self.main_window.show_error("Query failed", str(exc))
            self.main_window.update_status(STATUS_QUERY_FAILED)
    
    def _handle_clear_results(self) -> None:
        """Handle clear results request from UI."""
        self.main_window.clear_results()
        if self._is_connected and self.database_connection.is_connected:
            self.main_window.update_status("Results cleared.")
        else:
            self.main_window.update_status(STATUS_NOT_CONNECTED)
    
    def run(self) -> None:
        """Run the application."""
        self.main_window.run()
    
    def cleanup(self) -> None:
        """Clean up resources before application exit."""
        # Close database connection
        self.database_connection.close()
        self._is_connected = False


def main() -> None:
    """
    Application entry point.
    
    This function is called when the application is executed directly
    or through the module entry point.
    """
    app = PySQLApplication()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # Handle any uncaught exceptions
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Fatal Error", f"An unexpected error occurred: {e}")
        root.destroy()
    finally:
        # Ensure cleanup on exit
        app.cleanup()


if __name__ == "__main__":
    main()