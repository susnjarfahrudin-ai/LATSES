"""User-owned persistent product catalog entries.

The canonical catalog remains code-defined. User-entered manufacturer
specifications are stored separately in the per-user application data
location so they survive GUI restarts without mutating the repository seed.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import asdict
from pathlib import Path
from tempfile import NamedTemporaryFile

from lat_ces.building.model import Material

from .product_catalog import ProductSpec, categories, get_product


DEFAULT_CATALOG_FILENAME = "product_catalog_user.json"


def default_user_catalog_path() -> Path:
    """Return the platform-appropriate per-user LAT-CES catalog path."""
    root = os.environ.get("LOCALAPPDATA") or os.environ.get("XDG_DATA_HOME")
    base = Path(root) if root else Path.home() / ".local" / "share"
    return base / "LAT-CES" / DEFAULT_CATALOG_FILENAME


class UserProductCatalog:
    """Small JSON-backed store for user-entered ProductSpec records."""

    def __init__(self, path: str | os.PathLike[str] | None = None) -> None:
        self.path = Path(path) if path is not None else default_user_catalog_path()
        self._products: dict[str, ProductSpec] = {}
        self.reload()

    def reload(self) -> None:
        self._products = {}
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return
        if not isinstance(payload, list):
            return
        for item in payload:
            product = self._from_json(item)
            if product is not None:
                self._products[product.product_id] = product

    def all_products(self) -> tuple[ProductSpec, ...]:
        return tuple(self._products.values())

    def add_material(self, material: Material) -> ProductSpec:
        """Persist one validated Material as a user-declared catalog product."""
        category = (material.category or "").strip()
        manufacturer = (material.manufacturer or "").strip()
        product_id = (material.product_id or "").strip()
        if category not in categories():
            raise ValueError("Kategorija mora biti jedna od postojećih kategorija kataloga.")
        if not manufacturer or not product_id:
            raise ValueError("Proizvođač i Product ID su obavezni za katalog.")
        if get_product(product_id) is not None:
            raise ValueError(f"Product ID već postoji u osnovnom katalogu: {product_id}")
        if not any(
            value is not None
            for value in (
                material.density,
                material.youngs_modulus,
                material.thermal_conductivity,
                material.compressive_strength_mpa,
            )
        ):
            raise ValueError("Najmanje jedno fizičko svojstvo je obavezno za katalog.")
        product = ProductSpec(
            product_id=product_id,
            name=material.name,
            category=category,
            manufacturer=manufacturer,
            dimensions=", ".join(f"{value:g}" for value in material.dimensions_m) or None,
            density_kg_m3=material.density,
            youngs_modulus_pa=material.youngs_modulus,
            thermal_conductivity_w_mk=material.thermal_conductivity,
            compressive_strength_mpa=material.compressive_strength_mpa,
            status="USER_DECLARED",
            source="User-entered manufacturer specification",
        )
        existing = self._products.get(product.product_id)
        if existing is not None and existing != product:
            raise ValueError(f"Product ID već postoji u korisničkom katalogu: {product.product_id}")
        self._products[product.product_id] = product
        self._save()
        return product

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(product) for product in self._products.values()]
        with NamedTemporaryFile(
            "w", encoding="utf-8", dir=self.path.parent, delete=False, prefix=".product_catalog_"
        ) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        temp_path.replace(self.path)

    @staticmethod
    def _from_json(item: object) -> ProductSpec | None:
        if not isinstance(item, dict):
            return None
        try:
            product_id = item.get("product_id")
            name = item.get("name")
            category = item.get("category")
            manufacturer = item.get("manufacturer")
            if not all(isinstance(value, str) and value.strip() for value in (product_id, name, category, manufacturer)):
                return None
            if category not in categories() or get_product(product_id) is not None:
                return None
            numeric_fields = (
                "density_kg_m3",
                "youngs_modulus_pa",
                "thermal_conductivity_w_mk",
                "compressive_strength_mpa",
            )
            values: dict[str, float | None] = {}
            for field in numeric_fields:
                value = item.get(field)
                if value is not None:
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                        return None
                    values[field] = float(value)
                else:
                    values[field] = None
            return ProductSpec(
                product_id=product_id.strip(),
                name=name.strip(),
                category=category.strip(),
                manufacturer=manufacturer.strip(),
                dimensions=item.get("dimensions") if isinstance(item.get("dimensions"), str) else None,
                density_kg_m3=values["density_kg_m3"],
                youngs_modulus_pa=values["youngs_modulus_pa"],
                thermal_conductivity_w_mk=values["thermal_conductivity_w_mk"],
                compressive_strength_mpa=values["compressive_strength_mpa"],
                status="USER_DECLARED",
                source="User-entered manufacturer specification",
            )
        except (TypeError, ValueError, OverflowError):
            return None
