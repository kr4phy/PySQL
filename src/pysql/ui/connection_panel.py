"""
Connection panel component for PySQL.

This module provides the MySQL connection input controls and connection actions.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from pysql.core.config import (
    DEFAULT_HOST, 
    DEFAULT_PORT, 
    DEFAULT_USER
)


class ConnectionPanel:
    """
    Provides MySQL connection settings and connection controls.
    """
    
    def __init__(
        self, 
        parent: tk.Widget,
        on_connect: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the connection panel.
        
        Args:
            parent: Parent widget to contain this connection panel
            on_connect: Callback function when Connect is clicked
        """
        self.parent = parent
        self.on_connect_callback = on_connect
        
        # Create connection frame
        self.connection_frame = ttk.LabelFrame(parent, text="MySQL connection")
        self.connection_frame.pack(fill="x", padx=10, pady=(10, 6))
        
        # Create Tkinter variables for connection settings
        self.host_var = tk.StringVar(value=DEFAULT_HOST)
        self.port_var = tk.StringVar(value=str(DEFAULT_PORT))
        self.user_var = tk.StringVar(value=DEFAULT_USER)
        self.password_var = tk.StringVar()
        self.database_var = tk.StringVar()
        
        # Define connection fields
        fields = [
            ("Host", self.host_var, 16, False),
            ("Port", self.port_var, 6, False),
            ("User", self.user_var, 12, False),
            ("Password", self.password_var, 14, True),
            ("Database", self.database_var, 14, False),
        ]
        
        # Create field widgets
        for i, (label, variable, width, secret) in enumerate(fields):
            ttk.Label(
                self.connection_frame, 
                text=label
            ).grid(
                row=0, 
                column=i * 2, 
                padx=(8, 3), 
                pady=8, 
                sticky="w"
            )
            ttk.Entry(
                self.connection_frame, 
                textvariable=variable, 
                width=width,
                show="*" if secret else ""
            ).grid(
                row=0, 
                column=i * 2 + 1, 
                padx=(0, 8), 
                pady=8, 
                sticky="ew"
            )
        
        # Create connect button
        self.connect_button = ttk.Button(
            self.connection_frame, 
            text="Connect", 
            command=self._on_connect
        )
        self.connect_button.grid(row=0, column=10, padx=(2, 8), pady=8)
        
        # Configure grid weights
        self.connection_frame.columnconfigure(9, weight=1)
    
    def _on_connect(self) -> None:
        """Handle Connect button click."""
        if self.on_connect_callback:
            self.on_connect_callback()
    
    def get_connection_info(self) -> dict:
        """
        Get current connection information as a dictionary.
        
        Returns:
            Dictionary containing host, port, user, password, database
        """
        return {
            "host": self.host_var.get().strip(),
            "port": self.port_var.get().strip(),
            "user": self.user_var.get().strip(),
            "password": self.password_var.get(),
            "database": self.database_var.get().strip(),
        }
    
    def set_connection_info(
        self, 
        host: str, 
        port: str, 
        user: str, 
        password: str = "", 
        database: str = ""
    ) -> None:
        """
        Set connection information.
        
        Args:
            host: MySQL host
            port: MySQL port
            user: MySQL username
            password: MySQL password
            database: Optional MySQL database
        """
        self.host_var.set(host)
        self.port_var.set(port)
        self.user_var.set(user)
        self.password_var.set(password)
        self.database_var.set(database)
    
    def get_frame(self) -> ttk.LabelFrame:
        """Get the connection frame widget."""
        return self.connection_frame
    
    def update_connect_button_text(self, text: str) -> None:
        """Update the connect button text."""
        self.connect_button.config(text=text)