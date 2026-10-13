"""
Results view component for PySQL.

This module provides the result table with column configuration and scrolling.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Tuple, Optional


class ResultsView:
    """
    Displays query results in a table with horizontal and vertical scrolling.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the results view.
        
        Args:
            parent: Parent widget to contain this results view
        """
        self.parent = parent
        self._frame = ttk.LabelFrame(parent, text="Results")
        self._frame.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        
        # Create Treeview for results
        self.tree = ttk.Treeview(self._frame, show="headings")
        
        # Create scrollbars
        self.yscroll = ttk.Scrollbar(
            self._frame, 
            orient="vertical", 
            command=self.tree.yview
        )
        self.xscroll = ttk.Scrollbar(
            self._frame, 
            orient="horizontal", 
            command=self.tree.xview
        )
        
        # Configure treeview to use scrollbars
        self.tree.configure(
            yscrollcommand=self.yscroll.set, 
            xscrollcommand=self.xscroll.set
        )
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.yscroll.grid(row=0, column=1, sticky="ns")
        self.xscroll.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        self._frame.rowconfigure(0, weight=1)
        self._frame.columnconfigure(0, weight=1)
    
    def display_results(
        self, 
        columns: List[str], 
        formatted_rows: List[Tuple[str, ...]]
    ) -> None:
        """
        Display query results in the table.
        
        Args:
            columns: List of column names
            formatted_rows: List of formatted row tuples for display
        """
        # Clear existing data
        self.clear_results()
        
        # Set columns
        self.tree["columns"] = columns
        
        # Configure column headings and widths
        for column in columns:
            self.tree.heading(column, text=column)
            self.tree.column(
                column, 
                width=160, 
                minwidth=70, 
                stretch=True, 
                anchor="w"
            )
        
        # Insert formatted rows
        for row in formatted_rows:
            self.tree.insert("", "end", values=row)
    
    def clear_results(self) -> None:
        """Clear all results from the table."""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()
    
    def get_frame(self) -> ttk.LabelFrame:
        """Get the frame widget for this results view."""
        return self._frame
    
    def pack(self, **kwargs) -> None:
        """Pack the results view frame."""
        self._frame.pack(**kwargs)
    
    def pack_forget(self) -> None:
        """Unpack the results view frame."""
        self._frame.pack_forget()