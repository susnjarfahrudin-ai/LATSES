"""Dedicated physical material input boundary for the desktop GUI.

The dialog collects a complete Material record, applies the mandatory
Manufacturer Specification Gate, validates user-entered values through the
canonical Material dataclass, and returns the resulting object to the caller.
It does not mutate BuildingModel directly; the caller remains the owner of
model admission/persistence.
"""
from __future__ import annotations

import math
import tkinter as tk
import unicodedata
from tkinter import messagebox, ttk
from typing import Callable, Sequence

from lat_ces.building.model import Material


MANUFACTURER_SPECIFICATION_REQUIRED = (
    "Proizvođačka specifikacija je obavezna: unesite proizvođača, Product ID "
    "(oznaku/model) i kategoriju materijala."
)
PHYSICAL_PROPERTY_REQUIRED = (
    "Najmanje jedno relevantno fizičko svojstvo je obavezno: gustina, E, λ "
    "ili pritisna čvrstoća."
)
INPUT_THREAT_REJECTED = "Ulaz je odbijen: podatak nije dozvoljen na input granici."
_MAX_TEXT_LENGTH = 256
_MAX_DIMENSION_COUNT = 6
_MAX_INPUT_FIELD_COUNT = 16
_ALLOWED_INPUT_FIELDS = {
    "name", "category", "manufacturer", "product_id", "density",
    "youngs_modulus", "poisson_ratio", "thermal_conductivity",
    "compressive_strength_mpa", "dimensions",
}


def _safe_text(value: str, label: str) -> str:
    """Normalize bounded user text and reject control characters."""
    if not isinstance(value, str):
        raise ValueError(f"{label} mora biti tekst.")
    normalized = unicodedata.normalize("NFKC", value).strip()
    if len(normalized) > _MAX_TEXT_LENGTH:
        raise ValueError(f"{label} je predug (maksimalno {_MAX_TEXT_LENGTH} znakova).")
    if any(unicodedata.category(char).startswith("C") for char in normalized):
        raise ValueError(f"{INPUT_THREAT_REJECTED} {label} sadrži nedozvoljene kontrolne znakove.")
    return normalized


def _optional_float(value: str, label: str) -> float | None:
    text = _safe_text(value, label)
    if not text:
        return None
    try:
        result = float(text)
    except ValueError as exc:
        raise ValueError(f"{label} mora biti broj ili prazno.") from exc
    if not math.isfinite(result):
        raise ValueError(f"{label} mora biti konačan broj.")
    return result


def _dimensions(value: str) -> tuple[float, ...]:
    text = _safe_text(value, "Dimenzije")
    if not text:
        return ()
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if len(parts) > _MAX_DIMENSION_COUNT:
        raise ValueError(f"Dimenzije mogu sadržavati najviše {_MAX_DIMENSION_COUNT} vrijednosti.")
    result = []
    for part in parts:
        try:
            number = float(part)
        except ValueError as exc:
            raise ValueError("Dimenzije moraju biti konačni brojevi odvojeni zarezom.") from exc
        if not math.isfinite(number) or number <= 0:
            raise ValueError("Dimenzije materijala moraju biti konačni brojevi > 0.")
        result.append(number)
    return tuple(result)


def validate_manufacturer_specification(fields: dict[str, str]) -> None:
    """Apply the minimum identity/specification gate before Material creation."""
    if not isinstance(fields, dict) or len(fields) > _MAX_INPUT_FIELD_COUNT:
        raise ValueError(f"{INPUT_THREAT_REJECTED} Nevažeća struktura ulaznih polja.")
    unknown_fields = set(fields) - _ALLOWED_INPUT_FIELDS
    if unknown_fields:
        raise ValueError(
            f"{INPUT_THREAT_REJECTED} Nevažeća struktura ulaznih polja: "
            f"{', '.join(sorted(map(str, unknown_fields)))}."
        )

    name = _safe_text(fields.get("name", ""), "Naziv")
    category = _safe_text(fields.get("category", ""), "Kategorija")
    manufacturer = _safe_text(fields.get("manufacturer", ""), "Proizvođač")
    product_id = _safe_text(fields.get("product_id", ""), "Product ID")

    missing = []
    if not name:
        missing.append("Naziv")
    if not category:
        missing.append("Kategorija")
    if not manufacturer:
        missing.append("Proizvođač")
    if not product_id:
        missing.append("Product ID / oznaka proizvođača")
    if missing:
        raise ValueError(f"{MANUFACTURER_SPECIFICATION_REQUIRED} Nedostaje: {', '.join(missing)}.")

    physical = (
        _safe_text(fields.get("density", ""), "Gustina"),
        _safe_text(fields.get("youngs_modulus", ""), "Modul E"),
        _safe_text(fields.get("thermal_conductivity", ""), "Toplotna provodljivost λ"),
        _safe_text(fields.get("compressive_strength_mpa", ""), "Pritisna čvrstoća"),
    )
    if not any(physical):
        raise ValueError(PHYSICAL_PROPERTY_REQUIRED)


def material_from_fields(fields: dict[str, str]) -> Material:
    """Build one canonical Material after the mandatory input/security gate."""
    validate_manufacturer_specification(fields)
    return Material(
        name=_safe_text(fields["name"], "Naziv"),
        density=_optional_float(fields.get("density", ""), "Gustina"),
        youngs_modulus=_optional_float(fields.get("youngs_modulus", ""), "Modul elastičnosti E"),
        poisson_ratio=_optional_float(fields.get("poisson_ratio", ""), "Poissonov koeficijent ν"),
        thermal_conductivity=_optional_float(fields.get("thermal_conductivity", ""), "Toplotna provodljivost λ"),
        product_id=_safe_text(fields["product_id"], "Product ID"),
        manufacturer=_safe_text(fields["manufacturer"], "Proizvođač"),
        dimensions_m=_dimensions(fields.get("dimensions", "")),
        compressive_strength_mpa=_optional_float(fields.get("compressive_strength_mpa", ""), "Pritisna čvrstoća"),
        category=_safe_text(fields["category"], "Kategorija"),
    )


class MaterialInputDialog(tk.Toplevel):
    """Modal physical-material editor with a mandatory specification gate."""

    _FIELDS = (
        ("name", "Naziv", True),
        ("category", "Kategorija", True),
        ("manufacturer", "Proizvođač", True),
        ("product_id", "Product ID / oznaka proizvođača", True),
        ("density", "Gustina (kg/m³)", False),
        ("youngs_modulus", "Modul E (Pa)", False),
        ("poisson_ratio", "Poisson ν (-)", False),
        ("thermal_conductivity", "Toplotna provodljivost λ (W/mK)", False),
        ("compressive_strength_mpa", "Pritisna čvrstoća (MPa)", False),
        ("dimensions", "Dimenzije (m, zarez)", False),
    )

    def __init__(
        self,
        parent: tk.Misc,
        on_material: Callable[[Material], None],
        category_values: Sequence[str] | None = None,
    ) -> None:
        super().__init__(parent)
        self._on_material = on_material
        self._category_values = tuple(category_values or ())
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
            text="Manufacturer Specification Gate: identitet proizvođača, oznaka proizvoda i kategorija moraju biti poznati prije unosa. Najmanje jedno fizičko svojstvo mora biti navedeno. Ulaz se tretira kao nepouzdan podatak dok ne prođe validaciju.",
            wraplength=560,
            foreground="#92400e",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        self._vars: dict[str, tk.StringVar] = {}
        for row, (key, label, required) in enumerate(self._FIELDS, start=2):
            self._vars[key] = tk.StringVar()
            ttk.Label(body, text=f"{label}{' *' if required else ''}").grid(row=row, column=0, sticky="w", pady=3)
            if key == "category" and self._category_values:
                widget = ttk.Combobox(
                    body,
                    textvariable=self._vars[key],
                    state="readonly",
                    values=self._category_values,
                    width=40,
                )
                widget.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=3)
                widget.current(0)
            else:
                ttk.Entry(body, textvariable=self._vars[key], width=42).grid(
                    row=row, column=1, sticky="ew", padx=(12, 0), pady=3
                )

        actions = ttk.Frame(body)
        actions.grid(row=len(self._FIELDS) + 2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(actions, text="Otkaži", command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(actions, text="Dodaj u katalog", command=self._submit).pack(side="right")

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
