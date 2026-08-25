"""Canonical contextual properties/results panel for LAT-CES.

This widget is intentionally presentation-only. It reads a supplied context
mapping and never owns BuildingModel state or performs engineering math.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Mapping, Any


class PropertiesPanel(ttk.LabelFrame):
    """Compact context-sensitive inspector for the canonical GUI."""

    def __init__(self, parent: tk.Misc, *, title: str = "Properties / Results") -> None:
        super().__init__(parent, text=title, padding=8)
        self._rows: dict[str, ttk.Label] = {}
        self._empty = ttk.Label(self, text="Nije odabran objekat", wraplength=280)
        self._empty.pack(fill="x")

    def clear(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        self._rows.clear()
        self._empty = ttk.Label(self, text="Nije odabran objekat", wraplength=280)
        self._empty.pack(fill="x")

    def show_context(self, sections: Mapping[str, Mapping[str, Any]]) -> None:
        """Render ordered sections of display-ready values."""
        for child in self.winfo_children():
            child.destroy()
        self._rows.clear()

        first = True
        for section_name, values in sections.items():
            if not values:
                continue
            frame = ttk.LabelFrame(self, text=section_name, padding=6)
            frame.pack(fill="x", pady=(0 if first else 6, 0))
            first = False
            for key, value in values.items():
                row = ttk.Frame(frame)
                row.pack(fill="x", pady=1)
                ttk.Label(row, text=f"{key}:", width=20, anchor="w").pack(side="left")
                label = ttk.Label(row, text=self._format_value(value), anchor="e")
                label.pack(side="right", fill="x", expand=True)
                self._rows[f"{section_name}.{key}"] = label

        if first:
            self._empty = ttk.Label(self, text="Nema podataka za prikaz", wraplength=280)
            self._empty.pack(fill="x")

    @staticmethod
    def _format_value(value: Any) -> str:
        if isinstance(value, bool):
            return "DA" if value else "NE"
        if value is None:
            return "—"
        return str(value)


__all__ = ["PropertiesPanel"]
