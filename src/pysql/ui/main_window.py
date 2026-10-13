"""
Main window component for PySQL.

This module provides the main application window and UI composition.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from pysql.core.config import (
    APP_TITLE,
    DEFAULT_WINDOW_WIDTH,
    DEFAULT_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    STATUS_NOT_CONNECTED
)
from .connection_panel import ConnectionPanel
from .options_panel import OptionsPanel
from .query_editor import QueryEditor
from .results_view import ResultsView


class MainWindow:
    """
    Main application window for PySQL.
    
    This class composes all UI components and manages their interaction.
    """
    
    def __init__(
        self,
        on_connect: Optional[Callable[[dict], None]] = None,
        on_execute_query: Optional[Callable[[str, bool], None]] = None,
        on_clear_results: Optional[Callable[[], None]] = None
    ):
        """
        Initialize the main window.
        
        Args:
            on_connect: Callback for connection attempts with connection info
            on_execute_query: Callback for query execution with SQL and quote formatting flag
            on_clear_results: Callback for clearing results
        """
        # Create main window
        self.root = tk.Tk()
        self.root.title(APP_TITLE)
        self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        
        # Store callbacks
        self.on_connect_callback = on_connect
        self.on_execute_query_callback = on_execute_query
        self.on_clear_results_callback = on_clear_results
        
        # Create UI components
        self.connection_panel = ConnectionPanel(
            self.root, 
            on_connect=self._handle_connect
        )
        
        self.options_panel = OptionsPanel(self.root)
        
        self.query_editor = QueryEditor(
            self.root,
            on_execute=self._handle_execute_query,
            on_clear=self._handle_clear_results
        )
        
        self.results_view = ResultsView(self.root)
        
        # Create status bar
        self.status_var = tk.StringVar(value=STATUS_NOT_CONNECTED)
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief="sunken", 
            anchor="w"
        )
        self.status_bar.pack(fill="x", side="bottom")
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _handle_connect(self) -> None:
        """Handle connection request from connection panel."""
        if self.on_connect_callback:
            connection_info = self.connection_panel.get_connection_info()
            self.on_connect_callback(connection_info)
    
    def _handle_execute_query(self) -> None:
        """Handle query execution request from query editor."""
        if self.on_execute_query_callback:
            sql = self.query_editor.get_query()
            quote_formatting = self.options_panel.get_quote_formatting_enabled()
            self.on_execute_query_callback(sql, quote_formatting)
    
    def _handle_clear_results(self) -> None:
        """Handle clear results request from query editor."""
        if self.on_clear_results_callback:
            self.on_clear_results_callback()
    
    def _on_close(self) -> None:
        """Handle window close event."""
        self.root.destroy()
    
    def update_status(self, message: str) -> None:
        """Update the status bar message."""
        self.status_var.set(message)
    
    def show_error(self, title: str, message: str) -> None:
        """Show an error message dialog."""
        messagebox.showerror(title, message)
    
    def show_info(self, title: str, message: str) -> None:
        """Show an information message dialog."""
        messagebox.showinfo(title, message)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show a warning message dialog."""
        messagebox.showwarning(title, message)
    
    def display_results(
        self, 
        columns: list, 
        formatted_rows: list
    ) -> None:
        """Display query results in the results view."""
        self.results_view.display_results(columns, formatted_rows)
    
    def clear_results(self) -> None:
        """Clear the results view."""
        self.results_view.clear_results()
    
    def run(self) -> None:
        """Run the main application loop."""
        self.root.mainloop()
    
    def destroy(self) -> None:
        """Destroy the main window."""
        self.root.destroy()
    
    def get_root(self) -> tk.Tk:
        """Get the underlying Tk root window."""
        return self.root