from __future__ import annotations

import os
import tkinter as tk

import pytest

from lat_ces.gui_properties import PropertiesPanel


def _gui_display_available() -> bool:
    """Return whether a real Tk display is available for the widget test."""
    if os.name != "nt" and not os.environ.get("DISPLAY"):
        return False
    try:
        root = tk.Tk()
    except tk.TclError:
        return False
    root.destroy()
    return True


@pytest.mark.skipif(not _gui_display_available(), reason="Tk display unavailable")
def test_properties_panel_renders_context_sections() -> None:
    root = tk.Tk()
    root.withdraw()
    try:
        panel = PropertiesPanel(root)
        panel.pack()
        panel.show_context(
            {
                "Geometrija": {"dužina": "4.2 m", "debljina": "0.2 m"},
                "Engineering": {"status": "CALCULATED"},
            }
        )
        assert panel._rows["Geometrija.dužina"]["text"] == "4.2 m"
        assert panel._rows["Engineering.status"]["text"] == "CALCULATED"
    finally:
        root.destroy()
