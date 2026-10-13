"""
Application configuration and constants for PySQL.
"""

from typing import Final

# Application metadata
APP_TITLE: Final[str] = "PySQL — MySQL Client"
APP_VERSION: Final[str] = "0.1.0"

# Default connection settings
DEFAULT_HOST: Final[str] = "127.0.0.1"
DEFAULT_PORT: Final[int] = 3306
DEFAULT_USER: Final[str] = "root"

# UI settings
DEFAULT_WINDOW_WIDTH: Final[int] = 1050
DEFAULT_WINDOW_HEIGHT: Final[int] = 700
MIN_WINDOW_WIDTH: Final[int] = 760
MIN_WINDOW_HEIGHT: Final[int] = 500

# Database settings
CONNECTION_TIMEOUT: Final[int] = 5

# Default query for the editor
DEFAULT_QUERY: Final[str] = (
    "SELECT 1 AS id, 'Kim Min-su' AS name, 'Robotics' AS club\n"
    "UNION ALL SELECT 2, 'Lee Seo-yeon', 'Cybersecurity'\n"
    "UNION ALL SELECT 3, 'Park Ji-hoon', 'Game Development';"
)

# Status messages
STATUS_NOT_CONNECTED: Final[str] = (
    "Not connected. Connect to a MySQL server to run queries."
)
STATUS_CONNECTION_FAILED: Final[str] = "Connection failed."
STATUS_QUERY_FAILED: Final[str] = "Query failed."
