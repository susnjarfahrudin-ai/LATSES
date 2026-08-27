"""Canonical product/material catalog for LAT-CES.

Starter entries deliberately distinguish VERIFIED, REFERENCE and MISSING data.
Missing manufacturer and engineering properties are never invented. Manufacturer
facts are accompanied by source/provenance metadata so engineering projections can
remain computable without pretending manufacturer data is independently verified.
"""
from __future__ import annotations

from dataclasses import dataclass


WIENERBERGER_POROTHERM_25_S_SOURCE = (
    "https://www.wienerberger.ba/content/dam/wienerberger/bosnia/marketing/"
    "documents-magazines/technical/porotherm/technical-product-info-sheet/"
    "BA_MKT_TEC_WAL_POR_Porotherm_25_S.pdf"
)


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
    source_uri: str | None = None
    source_document: str | None = None
    evidence_id: str | None = None
    canonical_product_id: str | None = None
    verification_note: str | None = None

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
    ProductSpec(
        "MASONRY-CONCRETE-25X20X40",
        "Betonski blok",
        "Zidovi",
        dimensions="25 × 20 × 40 cm",
        status="MISSING",
        source="LAT-CES starter catalog",
    ),
    ProductSpec(
        "MASONRY-THERMAL-25X25X30",
        "Termo blok — Porotherm 25 S referentni profil",
        "Zidovi",
        manufacturer="Wienerberger",
        dimensions="375 × 250 × 238 mm; zid d=250 mm",
        density_kg_m3=630.0,
        thermal_conductivity_w_mk=0.145,
        compressive_strength_mpa=10.0,
        status="REFERENCE",
        source="Wienerberger Bosnia official technical sheet",
        source_uri=WIENERBERGER_POROTHERM_25_S_SOURCE,
        source_document="Porotherm 25 S Tehnički list",
        evidence_id="EXT-WIENERBERGER-BA-POROTHERM-25S",
        canonical_product_id="MASONRY-POROTHERM-25-S",
        verification_note="Manufacturer-declared reference data; independent verification remains a separate gate.",
    ),
    ProductSpec(
        "CONCRETE-REFERENCE-C25-30",
        "Armirani beton C25/30 — referentni materijal",
        "Beton",
        density_kg_m3=2500.0,
        youngs_modulus_pa=30_000_000_000.0,
        thermal_conductivity_w_mk=2.10,
        compressive_strength_mpa=25.0,
        status="REFERENCE",
        source="LAT-CES reference engineering data",
    ),
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
)


def all_products() -> tuple[ProductSpec, ...]:
    return CATALOG


def categories() -> tuple[str, ...]:
    return tuple(dict.fromkeys(product.category for product in CATALOG))


def products_for_category(category: str) -> tuple[ProductSpec, ...]:
    return tuple(product for product in CATALOG if product.category == category)


def get_product(product_id: str) -> ProductSpec | None:
    return next((product for product in CATALOG if product.product_id == product_id), None)
