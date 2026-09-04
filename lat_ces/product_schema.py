"""Shared product schema used by the LAT-CES material catalog."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    material: Optional[str] = None
    dimensions: Optional[str] = None
    mass_kg_per_unit: Optional[float] = None
    density_kg_m3: Optional[float] = None
    thermal_conductivity_w_mk: Optional[float] = None
    acoustic_rating_db: Optional[float] = None
    price: Optional[float] = None
    manufacturer: Optional[str] = None
    source: Optional[str] = None
