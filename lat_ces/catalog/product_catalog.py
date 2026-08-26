"""Canonical product/material catalog for LAT-CES.

Starter entries deliberately distinguish VERIFIED, REFERENCE and MISSING data.
Missing manufacturer and engineering properties are never invented.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProductSpec:
    product_id: str
    name: str
    category: str
    manufacturer: str | None = None
    dimensions: str | None = None
    density_kg_m3: float | None = None
    youngs_modulus_pa: float | None = None
    thermal_conductivity_w_mk: float | None = None
    compressive_strength_mpa: float | None = None
    status: str = "MISSING"
    source: str | None = None

    @property
    def engineering_summary(self) -> str:
        parts = [self.name]
        if self.manufacturer:
            parts.append(self.manufacturer)
        if self.dimensions:
            parts.append(self.dimensions)
        parts.append(self.status)
        return " · ".join(parts)


CATALOG: tuple[ProductSpec, ...] = (
    ProductSpec("MASONRY-CONCRETE-25X20X40", "Betonski blok", "Zidovi", dimensions="25 × 20 × 40 cm", status="MISSING", source="LAT-CES starter catalog"),
    ProductSpec("MASONRY-THERMAL-25X25X30", "Termo blok", "Zidovi", dimensions="25 × 25 × 30 cm", status="MISSING", source="LAT-CES starter catalog"),
    ProductSpec("CONCRETE-REFERENCE-C25-30", "Armirani beton C25/30 — referentni materijal", "Beton", density_kg_m3=2500.0, youngs_modulus_pa=30_000_000_000.0, thermal_conductivity_w_mk=2.10, compressive_strength_mpa=25.0, status="REFERENCE", source="LAT-CES reference engineering data"),
    ProductSpec("INSULATION-GLASS-WOOL", "Staklena mineralna vuna", "Izolacija", status="MISSING", source="Exact manufacturer/product required"),
    ProductSpec("INSULATION-ROCK-WOOL", "Kamena mineralna vuna", "Izolacija", status="MISSING", source="Exact manufacturer/product required"),
    ProductSpec("INSULATION-EPS", "EPS / stiropor", "Izolacija", status="MISSING", source="Exact manufacturer/product required"),
    ProductSpec("WINDOW-PVC-TRIPLE", "PVC prozor — trostruko ostakljenje", "Prozori i vrata", status="MISSING", source="Exact product and Uw required"),
    ProductSpec("WINDOW-WOOD-ALU-TRIPLE", "Drvo/ALU prozor — trostruko ostakljenje", "Prozori i vrata", status="MISSING", source="Exact product and Uw required"),
    ProductSpec("DOOR-EXTERIOR-INSULATED", "Vanjska termoizolovana vrata", "Prozori i vrata", status="MISSING", source="Exact product and Ud required"),
    ProductSpec("UFH-PEX-16X2", "Podno grijanje — PEX cijev", "Podno grijanje", dimensions="16 × 2 mm", status="MISSING", source="Exact product and circuit data required"),
    ProductSpec("UFH-MANIFOLD-6", "Razdjelnik podnog grijanja — 6 krugova", "Podno grijanje", status="MISSING", source="Exact product required"),
    ProductSpec("VENT-EC-DUCT-FAN", "EC kanalni ventilator", "Ventilacija", status="MISSING", source="Exact airflow/pressure curve required"),
    ProductSpec("VENT-HRV-RESIDENTIAL", "Kućni rekuperator", "Ventilacija", status="MISSING", source="Exact airflow/efficiency required"),
    ProductSpec("VENT-DUCT-100", "Ventilacioni kanal", "Ventilacija", dimensions="Ø100 mm", status="MISSING", source="Exact product required"),
    ProductSpec("ESTRICH-CEMENT-50", "Cementni estrih", "Estrih", dimensions="50 mm referentna debljina", status="REFERENCE", source="LAT-CES reference floor-build-up option"),
    ProductSpec("ESTRICH-ANHYDRITE-50", "Anhidritni estrih", "Estrih", dimensions="50 mm referentna debljina", status="REFERENCE", source="LAT-CES reference floor-build-up option"),
    ProductSpec("FINISH-CERAMIC-GRES-10", "Keramika / gres", "Završni sloj", dimensions="10 mm referentna debljina", status="REFERENCE", source="LAT-CES reference floor-finish option"),
    ProductSpec("FINISH-LAMINATE-10", "Laminat", "Završni sloj", dimensions="10 mm referentna debljina", status="REFERENCE", source="LAT-CES reference floor-finish option"),
    ProductSpec("FINISH-PARKET-15", "Parket", "Završni sloj", dimensions="15 mm referentna debljina", status="REFERENCE", source="LAT-CES reference floor-finish option"),
    ProductSpec("FINISH-VINYL-5", "Vinil", "Završni sloj", dimensions="5 mm referentna debljina", status="REFERENCE", source="LAT-CES reference floor-finish option"),
)


def all_products() -> tuple[ProductSpec, ...]:
    return CATALOG


def categories() -> tuple[str, ...]:
    return tuple(dict.fromkeys(product.category for product in CATALOG))


def products_for_category(category: str) -> tuple[ProductSpec, ...]:
    return tuple(product for product in CATALOG if product.category == category)


def get_product(product_id: str) -> ProductSpec | None:
    return next((product for product in CATALOG if product.product_id == product_id), None)
