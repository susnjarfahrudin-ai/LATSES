"""Dedicated physical material input boundary for the desktop GUI.

The dialog collects a complete Material record, validates user-entered values
through the canonical Material dataclass, and returns the resulting object to
the caller. It does not mutate BuildingModel directly; the caller remains the
owner of model admission/persistence.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from lat_ces.building.model import Material


def _optional_float(value: str, label: str) -> float | None:
    text = value.strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"{label} mora biti broj ili prazno.") from exc


def _dimensions(value: str) -> tuple[float, ...]:
    text = value.strip()
    if not text:
        return ()
    try:
        result = tuple(float(part.strip()) for part in text.split(",") if part.strip())
    except ValueError as exc:
        raise ValueError("Dimenzije moraju biti brojevi odvojeni zarezom.") from exc
    if any(item <= 0 for item in result):
        raise ValueError("Dimenzije materijala moraju biti > 0.")
    return result


def material_from_fields(fields: dict[str, str]) -> Material:
    """Build one canonical Material from physical GUI fields."""
    name = fields.get("name", "").strip()
    if not name:
        raise ValueError("Naziv materijala je obavezan.")
    return Material(
        name=name,
        density=_optional_float(fields.get("density", ""), "Gustina"),
        youngs_modulus=_optional_float(fields.get("youngs_modulus", ""), "Modul elastičnosti E"),
        poisson_ratio=_optional_float(fields.get("poisson_ratio", ""), "Poissonov koeficijent ν"),
        thermal_conductivity=_optional_float(fields.get("thermal_conductivity", ""), "Toplotna provodljivost λ"),
        product_id=fields.get("product_id", "").strip() or None,
        manufacturer=fields.get("manufacturer", "").strip() or None,
        dimensions_m=_dimensions(fields.get("dimensions", "")),
        compressive_strength_mpa=_optional_float(fields.get("compressive_strength_mpa", ""), "Pritisna čvrstoća"),
        category=fields.get("category", "").strip() or None,
    )


class MaterialInputDialog(tk.Toplevel):
    """Modal physical-material editor returning a Material through callback."""

    _FIELDS = (
        ("name", "Naziv", True),
        ("category", "Kategorija", False),
        ("manufacturer", "Proizvođač", False),
        ("product_id", "Product ID", False),
        ("density", "Gustina (kg/m³)", False),
        ("youngs_modulus", "Modul E (Pa)", False),
        ("poisson_ratio", "Poisson ν (-)", False),
        ("thermal_conductivity", "Toplotna provodljivost λ (W/mK)", False),
        ("compressive_strength_mpa", "Pritisna čvrstoća (MPa)", False),
        ("dimensions", "Dimenzije (m, zarez)", False),
    )

    def __init__(self, parent: tk.Misc, on_material: Callable[[Material], None]) -> None:
        super().__init__(parent)
        self._on_material = on_material
        self.title("LAT-CES — Novi materijal")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        body = ttk.Frame(self, padding=14)
        body.pack(fill="both", expand=True)
        ttk.Label(body, text="Fizički unos novog materijala", font=("Segoe UI", 12, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        ttk.Label(
            body,
            text="Podaci se prvo pretvaraju u jedan Material zapis; proračunski moduli ga kasnije čitaju kroz svoje ulazne granice.",
            wraplength=520,
            foreground="#475569",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self._vars: dict[str, tk.StringVar] = {}
        for row, (key, label, required) in enumerate(self._FIELDS, start=2):
            self._vars[key] = tk.StringVar()
            ttk.Label(body, text=f"{label}{' *' if required else ''}").grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(body, textvariable=self._vars[key], width=42).grid(
                row=row, column=1, sticky="ew", padx=(12, 0), pady=3
            )

        actions = ttk.Frame(body)
        actions.grid(row=len(self._FIELDS) + 2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Otkaži", command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(actions, text="Dodaj materijal", command=self._submit).pack(side="right")

        self.bind("<Return>", lambda _event: self._submit())
        self.bind("<Escape>", lambda _event: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _submit(self) -> None:
        fields = {key: var.get() for key, var in self._vars.items()}
        try:
            material = material_from_fields(fields)
            self._on_material(material)
        except (TypeError, ValueError) as exc:
            messagebox.showwarning("LAT-CES — Materijal", str(exc), parent=self)
            return
        self.destroy()
