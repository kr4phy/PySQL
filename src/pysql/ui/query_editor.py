"""
Query editor component for PySQL.

This module provides the SQL query editor with execution controls.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from pysql.core.config import DEFAULT_QUERY


class QueryEditor:
    """
    Provides SQL query editing and execution controls.
    """
    
    def __init__(
        self, 
        parent: tk.Widget,
        default_query: Optional[str] = None,
        on_execute: Optional[Callable[[], None]] = None,
        on_clear: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the query editor.
        
        Args:
            parent: Parent widget to contain this query editor
            default_query: Default SQL query to display
            on_execute: Callback function when Run query is clicked
            on_clear: Callback function when Clear results is clicked
        """
        self.parent = parent
        self.on_execute_callback = on_execute
        self.on_clear_callback = on_clear
        
        # Create query frame
        self.query_frame = ttk.LabelFrame(parent, text="SQL query")
        self.query_frame.pack(fill="x", padx=10, pady=(0, 6))
        
        # Create text widget for query editing
        self.query_text = tk.Text(
            self.query_frame, 
            height=6, 
            wrap="none", 
            undo=True
        )
        self.query_text.pack(fill="both", expand=True, padx=6, pady=6)
        
        # Set default query
        query_to_display = default_query or DEFAULT_QUERY
        self.query_text.insert("1.0", query_to_display)
        
        # Create button frame
        self.button_frame = ttk.Frame(parent)
        self.button_frame.pack(fill="x", padx=10, pady=(0, 8))
        
        # Create buttons
        self.execute_button = ttk.Button(
            self.button_frame, 
            text="Run query", 
            command=self._on_execute
        )
        self.execute_button.pack(side="left")
        
        self.clear_button = ttk.Button(
            self.button_frame, 
            text="Clear results", 
            command=self._on_clear
        )
        self.clear_button.pack(side="left", padx=(6, 0))
        
        # Create info label
        self.info_label = ttk.Label(
            self.button_frame,
            text="Demo query works after connecting to MySQL; edit it to query your tables."
        )
        self.info_label.pack(side="left", padx=12)
    
    def _on_execute(self) -> None:
        """Handle Run query button click."""
        if self.on_execute_callback:
            self.on_execute_callback()
    
    def _on_clear(self) -> None:
        """Handle Clear results button click."""
        if self.on_clear_callback:
            self.on_clear_callback()
    
    def get_query(self) -> str:
        """Get the current SQL query text."""
        return self.query_text.get("1.0", "end-1c").strip()
    
    def set_query(self, query: str) -> None:
        """Set the SQL query text."""
        self.query_text.delete("1.0", "end")
        self.query_text.insert("1.0", query)
    
    def clear_query(self) -> None:
        """Clear the SQL query text."""
        self.query_text.delete("1.0", "end")
    
    def get_query_frame(self) -> ttk.LabelFrame:
        """Get the query frame widget."""
        return self.query_frame
    
    def get_button_frame(self) -> ttk.Frame:
        """Get the button frame widget."""
        return self.button_frame