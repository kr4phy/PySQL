"""
Options panel component for PySQL.

This module provides display options for the application.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional


class OptionsPanel:
    """
    Provides display options for the application.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the options panel.
        
        Args:
            parent: Parent widget to contain this options panel
        """
        self.parent = parent
        
        # Create options frame
        self.options_frame = ttk.Frame(parent)
        self.options_frame.pack(fill="x", padx=10, pady=(0, 6))
        
        # Create quote formatting option
        self.quote_var = tk.BooleanVar(value=True)
        
        self.quote_checkbutton = ttk.Checkbutton(
            self.options_frame,
            text="Display text values with single quotes (SQL-literal style)",
            variable=self.quote_var,
        )
        self.quote_checkbutton.pack(side="left")
        
        self.info_label = ttk.Label(
            self.options_frame,
            text="This changes display only; it does not modify database values.",
        )
        self.info_label.pack(side="left", padx=(12, 0))
    
    def get_quote_formatting_enabled(self) -> bool:
        """Check if quote formatting is enabled."""
        return self.quote_var.get()
    
    def set_quote_formatting_enabled(self, enabled: bool) -> None:
        """Set quote formatting enabled/disabled."""
        self.quote_var.set(enabled)
    
    def get_frame(self) -> ttk.Frame:
        """Get the options frame widget."""
        return self.options_frame