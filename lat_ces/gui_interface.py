"""Minimal LAT-CES interface foundation.

This module intentionally does not modify or import legacy GUI tabs. It defines
only the new shell and its tab-to-context contract.
"""

from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from typing import Final


TABS: Final[tuple[str, ...]] = (
    "MODEL OBJEKTA",
    "MATERIJAL OBJEKTA",
    "KONSTRUKCIJA OBJEKTA",
    "STATIKA OBJEKTA",
    "MEP OBJEKTA",
    "ILUSTRACIJA OBJEKTA",
    "MJERENJA U OBJEKTU",
)

TAB_OPTIONS: Final[dict[str, tuple[str, ...]]] = {
    "MODEL OBJEKTA": ("Temelj", "Tlocrt i etaže", "Prostorije", "Orijentacija", "Krov"),
    "MATERIJAL OBJEKTA": ("Katalog proizvoda", "Zidovi", "Ploče", "Pod", "Izolacija", "Stolarija"),
    "KONSTRUKCIJA OBJEKTA": ("Međuspratna konstrukcija", "Krovna konstrukcija", "Podkonstrukcija", "Veze etaža"),
    "STATIKA OBJEKTA": ("Lokacija", "Snijeg", "Vjetar", "Kiša", "Opterećenja", "Proračun"),
    "MEP OBJEKTA": ("Grijanje", "Hlađenje", "Voda", "Ventilacija", "Elektrika", "Akustika"),
    "ILUSTRACIJA OBJEKTA": ("Vanjski prikaz", "Unutrašnjost", "3D", "Tokovi zraka i vode", "Statika"),
    "MJERENJA U OBJEKTU": ("Zrak", "Voda", "Svjetlost", "Temperatura", "Vlaga", "CO₂", "Buka"),
}


@dataclass(frozen=True)
class InterfaceFoundation:
    """Machine-readable contract for the new GUI shell."""

    tabs: tuple[str, ...] = TABS
    left_panel: str = "TAB OPTIONS"
    center_panel: str = "REFERENCE HOUSE / WORKSPACE"
    right_panel: str = "KIŠOBRAN"
    natural_background: bool = True
    model_first: bool = True


class LatCesInterface(tk.Tk):
    """Small, dependency-free visual shell for the consolidated LAT-CES UI."""

    def __init__(self) -> None:
        super().__init__()
        self.title("LAT-CES — Interface Foundation")
        self.geometry("1400x820")
        self.minsize(1000, 650)
        self._build()

    def _build(self) -> None:
        self.configure(bg="#eaf4f8")
        header = tk.Frame(self, bg="#dceff7", height=64)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="LAT-CES", font=("Segoe UI", 18, "bold"), bg="#dceff7", fg="#173b4d").pack(side="left", padx=18)
        for tab in TABS:
            tk.Button(header, text=tab, relief="flat", bg="#dceff7", fg="#244b5c", activebackground="#c9e7f2", command=lambda name=tab: self._select_tab(name)).pack(side="left", padx=2, pady=12)

        body = tk.Frame(self, bg="#eaf4f8")
        body.pack(fill="both", expand=True, padx=12, pady=12)
        self.left = tk.Frame(body, width=240, bg="#f4f8f9", bd=1, relief="solid")
        self.left.pack(side="left", fill="y", padx=(0, 10))
        self.left.pack_propagate(False)
        self.left_title = tk.Label(self.left, text="TAB OPTIONS", font=("Segoe UI", 12, "bold"), bg="#f4f8f9", fg="#244b5c")
        self.left_title.pack(anchor="w", padx=14, pady=14)
        self.option_list = tk.Listbox(self.left, relief="flat", bd=0, bg="#f4f8f9", fg="#315565", highlightthickness=0)
        self.option_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.center = tk.Frame(body, bg="#dff2f7", bd=1, relief="solid")
        self.center.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(self.center, text="REFERENCE HOUSE\n\nCentral model / working space\n\nThe building model remains the single source of identity.", font=("Segoe UI", 16), bg="#dff2f7", fg="#315565", justify="center").pack(expand=True)

        self.right = tk.Frame(body, width=210, bg="#f4f8f9", bd=1, relief="solid")
        self.right.pack(side="right", fill="y")
        self.right.pack_propagate(False)
        tk.Label(self.right, text="☂", font=("Segoe UI Symbol", 52), bg="#f4f8f9", fg="#315565").pack(pady=(34, 8))
        tk.Label(self.right, text="KIŠOBRAN", font=("Segoe UI", 12, "bold"), bg="#f4f8f9", fg="#244b5c").pack()
        self.status = tk.Label(self.right, text="Model status\nready", font=("Segoe UI", 10), bg="#f4f8f9", fg="#315565", justify="center")
        self.status.pack(pady=18)
        self._select_tab(TABS[0])

    def _select_tab(self, name: str) -> None:
        self.left_title.configure(text=name)
        self.option_list.delete(0, tk.END)
        for option in TAB_OPTIONS[name]:
            self.option_list.insert(tk.END, option)
        self.status.configure(text=f"Model status\n{name}\nready")


def main() -> None:
    LatCesInterface().mainloop()


__all__ = ["InterfaceFoundation", "LatCesInterface", "TABS", "TAB_OPTIONS", "main"]
