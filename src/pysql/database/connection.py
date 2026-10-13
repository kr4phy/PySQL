"""
MySQL connection management for PySQL.

This module handles database connection lifecycle including establishment,
reconnection, and disconnection.
"""

from typing import Optional, Any
import mysql.connector
from mysql.connector import connection as mysql_connection
from mysql.connector import Error as MySQLError


class DatabaseConnection:
    """
    Manages MySQL database connection lifecycle.
    
    This class provides explicit connection management without exposing
    credentials in logs or error messages unnecessarily.
    """
    
    def __init__(self):
        """Initialize with no active connection."""
        self._connection: Optional[mysql_connection.MySQLConnection] = None
    
    @property
    def connection(self) -> Optional[mysql_connection.MySQLConnection]:
        """Get the current connection object."""
        return self._connection
    
    @property
    def is_connected(self) -> bool:
        """Check if there is an active, connected connection."""
        return self._connection is not None and self._connection.is_connected()
    
    def connect(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: Optional[str] = None,
        connection_timeout: int = 5
    ) -> str:
        """
        Establish a connection to the MySQL server.
        
        Args:
            host: MySQL server hostname or IP address
            port: MySQL server port
            user: Username for authentication
            password: Password for authentication
            database: Optional database name to connect to
            connection_timeout: Connection timeout in seconds
        
        Returns:
            Status message indicating connection result.
        
        Raises:
            MySQLError: If connection fails
        """
        # Close existing connection if present
        self.close()
        
        self._connection = mysql_connection.MySQLConnection(
            host=host.strip() or "127.0.0.1",
            port=port,
            user=user.strip(),
            password=password,
            database=database.strip() if database else None,
            connection_timeout=connection_timeout,
        )
        
        return f"Connected to MySQL at {host.strip()}:{port}"
    
    def close(self) -> None:
        """Close the current connection if it exists and is connected."""
        if self.is_connected:
            try:
                self._connection.close()
            except Exception:
                # Silently ignore errors during connection close
                pass
        self._connection = None
    
    def reconnect(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: Optional[str] = None,
        connection_timeout: int = 5
    ) -> str:
        """
        Reconnect to the MySQL server with new connection parameters.
        
        This is equivalent to close() followed by connect().
        
        Args:
            host: MySQL server hostname or IP address
            port: MySQL server port
            user: Username for authentication
            password: Password for authentication
            database: Optional database name to connect to
            connection_timeout: Connection timeout in seconds
        
        Returns:
            Status message indicating connection result.
        
        Raises:
            MySQLError: If connection fails
        """
        return self.connect(host, port, user, password, database, connection_timeout)
