"""GUI view for the adopted LAT-ARCH-3D-001 architecture.

This module is presentation-only. It does not create a BuildingModel, perform
engineering calculations, or introduce a second source of engineering truth.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


ARCHITECTURE_DOCUMENT_ID = "LAT-ARCH-3D-001"
ARCHITECTURE_DOCUMENT_PATH = "docs/architecture/LAT-ARCH-3D-001.md"


ARCHITECTURE_LAYERS = (
    ("CANONICAL MODEL", "BuildingModel", "Sole owner of physical-object identity."),
    ("ENGINEERING CORE", "Engineering results", "Scientific authority for engineering interpretation."),
    ("MEASUREMENT", "Measurements", "Observed reality: value, unit, time, location and provenance."),
    ("VALIDATION", "Simulation ↔ measurement", "Comparison, deviation, tolerance and validation status."),
    ("VISUALIZATION", "2D / 3D / illustrations", "Representation only; never changes engineering truth."),
    ("EXTERNAL BACKENDS", "OpenFOAM · ParaView · Blender", "Specialized solver / inspection / rendering backends."),
)


class EngineeringArchitectureView(ttk.Frame):
    """Read-only GUI presentation of LAT-ARCH-3D-001."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self._build()

    def _build(self) -> None:
        ttk.Label(
            self,
            text="Engineering Visualization & Validation Architecture",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 2))
        ttk.Label(
            self,
            text=f"{ARCHITECTURE_DOCUMENT_ID}  ·  ADOPTED  ·  {ARCHITECTURE_DOCUMENT_PATH}",
            foreground="#64748b",
        ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 12))

        body = ttk.Frame(self, padding=(16, 4, 16, 16))
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        for index, (title, value, description) in enumerate(ARCHITECTURE_LAYERS):
            row, column = divmod(index, 2)
            card = ttk.LabelFrame(body, text=title, padding=12)
            card.grid(row=row, column=column, sticky="nsew", padx=(0, 10 if column == 0 else 0), pady=(0, 10))
            ttk.Label(card, text=value, font=("Segoe UI", 12, "bold")).pack(anchor="w")
            ttk.Label(card, text=description, wraplength=360, foreground="#475569").pack(anchor="w", pady=(6, 0))

        flow = ttk.LabelFrame(body, text="Canonical engineering flow", padding=12)
        flow.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        ttk.Label(
            flow,
            text=(
                "BuildingModel → Engineering Core → Measurement → Validation → "
                "Visualization Contract → 2D / 3D / CFD / Illustrations → external backends"
            ),
            font=("Segoe UI", 11, "bold"),
            wraplength=900,
        ).pack(anchor="w")
        ttk.Label(
            flow,
            text="External tools represent or solve specialized tasks. LATSES remains the engineering authority.",
            foreground="#475569",
            wraplength=900,
        ).pack(anchor="w", pady=(8, 0))


def create_engineering_architecture_view(master: tk.Misc, **kwargs) -> EngineeringArchitectureView:
    """Create the read-only architecture view without creating any new model."""
    return EngineeringArchitectureView(master, **kwargs)
