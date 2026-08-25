from __future__ import annotations

import tkinter as tk

import pytest

from lat_ces.gui_properties import PropertiesPanel


@pytest.mark.skipif(not tk.TkVersion, reason="Tk unavailable")
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
