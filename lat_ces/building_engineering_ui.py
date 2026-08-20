"""Canonical Building Engineering UI shell.

Layout contract:
- left: command/navigation panel
- top: calculation/engineering panel
- center: BuildingModel visualization host

The shell is intentionally model-driven. It does not create a second building
model and it does not copy reference-house geometry into a parallel state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import tkinter as tk
from tkinter import ttk

from lat_ces.building.model import BuildingModel


@dataclass(frozen=True)
class EngineeringMetric:
    label: str
    value: str


class BuildingEngineeringShell(ttk.Frame):
    """Reusable three-zone shell around one canonical BuildingModel."""

    COMMANDS = (
        ("Model", "model"),
        ("Katalog", "catalog"),
        ("Tlocrt", "floor_plan"),
        ("Presjek", "section"),
        ("3D", "3d"),
        ("Konstrukcija", "structure"),
        ("MEP", "mep"),
        ("Provjera", "validate"),
        ("Izvještaj", "report"),
    )

    def __init__(
        self,
        master: tk.Misc,
        model: BuildingModel,
        *,
        on_command: Callable[[str], None] | None = None,
        center: tk.Widget | None = None,
    ) -> None:
        super().__init__(master)
        self.model = model
        self.on_command = on_command or (lambda _command: None)
        self.metric_vars: dict[str, tk.StringVar] = {}
        self._build()
        if center is not None:
            self.attach_center(center)
        self.refresh_metrics()

    def _build(self) -> None:
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.command_panel = ttk.LabelFrame(self, text="Komande", padding=8)
        self.command_panel.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 8))

        ttk.Label(
            self.command_panel,
            text="BUILDING MODEL",
            font=("Segoe UI", 10, "bold"),
        ).pack(fill="x", pady=(0, 8))
        for label, command in self.COMMANDS:
            ttk.Button(
                self.command_panel,
                text=label,
                command=lambda c=command: self.on_command(c),
            ).pack(fill="x", pady=2)

        self.calculation_panel = ttk.LabelFrame(
            self, text="Matematika / Engineering", padding=8
        )
        self.calculation_panel.grid(row=0, column=1, sticky="ew", pady=(0, 8))
        for index in range(7):
            self.calculation_panel.columnconfigure(index, weight=1)

        metrics = (
            ("area", "Površina", "0.00 m²"),
            ("volume", "Zapremina", "0.00 m³"),
            ("levels", "Etaže", "0"),
            ("rooms", "Prostorije", "0"),
            ("elements", "Elementi", "0"),
            ("roof", "Krov", "—"),
            ("status", "Status", "READY"),
        )
        for column, (key, label, default) in enumerate(metrics):
            box = ttk.Frame(self.calculation_panel)
            box.grid(row=0, column=column, sticky="ew", padx=3)
            ttk.Label(box, text=label).pack(anchor="w")
            var = tk.StringVar(value=default)
            self.metric_vars[key] = var
            ttk.Label(box, textvariable=var, font=("Segoe UI", 10, "bold")).pack(anchor="w")

        self.center_host = ttk.Frame(self, relief="sunken", padding=4)
        self.center_host.grid(row=1, column=1, sticky="nsew")
        self.center_host.columnconfigure(0, weight=1)
        self.center_host.rowconfigure(0, weight=1)
        ttk.Label(
            self.center_host,
            text="BuildingModel — centralni prikaz",
            anchor="center",
        ).grid(row=0, column=0, sticky="nsew")

    def attach_center(self, widget: tk.Widget) -> None:
        for child in self.center_host.winfo_children():
            child.destroy()
        widget.grid(in_=self.center_host, row=0, column=0, sticky="nsew")

    def refresh_metrics(self) -> None:
        self.metric_vars["area"].set(f"{self.model.floor_area:.2f} m²")
        self.metric_vars["volume"].set(f"{self.model.volume:.2f} m³")
        self.metric_vars["levels"].set(str(len(self.model.levels)))
        self.metric_vars["rooms"].set(str(self.model.room_count))
        self.metric_vars["elements"].set(str(self.model.element_count))
        self.metric_vars["roof"].set(self.model.roof.roof_type if self.model.roof else "—")

    def set_status(self, status: str) -> None:
        self.metric_vars["status"].set(status)


class ReferenceHouseCommandBridge:
    """Minimal command adapter used by the existing reference-house GUI."""

    def __init__(self, callbacks: dict[str, Callable[[], None]] | None = None) -> None:
        self.callbacks = callbacks or {}

    def __call__(self, command: str) -> None:
        callback = self.callbacks.get(command)
        if callback is not None:
            callback()


__all__ = ["EngineeringMetric", "BuildingEngineeringShell", "ReferenceHouseCommandBridge"]
