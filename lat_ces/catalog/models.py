"""Canonical product/material identity models.

The catalog stores identity and provenance, not engineering decisions. External
open datasets (IFC/bSDD, EPD/LCA and manufacturer catalogs) can be adapted into
these records without creating a second Building Model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple


@dataclass(frozen=True)
class ProductIdentity:
    """Stable identity for a manufacturer-declared construction product."""

    product_id: str
    category: str
    manufacturer: Optional[str] = None
    product_name: Optional[str] = None
    model: Optional[str] = None
    manufacturer_id: Optional[str] = None
    product_uri: Optional[str] = None
    ifc_class: Optional[str] = None
    bsdd_uri: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.product_id.strip():
            raise ValueError("product_id cannot be empty")
        if not self.category.strip():
            raise ValueError("product category cannot be empty")


@dataclass(frozen=True)
class ProductProperty:
    """A declared product property with explicit unit and provenance."""

    name: str
    value: str
    unit: Optional[str] = None
    property_uri: Optional[str] = None
    source_uri: Optional[str] = None
    source_version: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("property name cannot be empty")
        if not self.value.strip():
            raise ValueError("property value cannot be empty")


@dataclass(frozen=True)
class ProductRecord:
    """Normalized product record consumed by Building Model adapters."""

    identity: ProductIdentity
    properties: Tuple[ProductProperty, ...] = ()
    dimensions_m: Tuple[float, ...] = ()
    source_uris: Tuple[str, ...] = ()
    dataset_id: Optional[str] = None
    dataset_version: Optional[str] = None
    license_name: Optional[str] = None
    license_uri: Optional[str] = None
    tags: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if any(value <= 0 for value in self.dimensions_m):
            raise ValueError("product dimensions must be positive")

    def property(self, name: str) -> Optional[ProductProperty]:
        for item in self.properties:
            if item.name == name:
                return item
        return None


@dataclass
class ProductRegistry:
    """In-memory identity registry; persistence belongs to a future data layer."""

    _records: dict[str, ProductRecord] = field(default_factory=dict)

    def add(self, record: ProductRecord) -> None:
        product_id = record.identity.product_id
        if product_id in self._records:
            raise ValueError(f"duplicate product id: {product_id}")
        self._records[product_id] = record

    def get(self, product_id: str) -> ProductRecord:
        try:
            return self._records[product_id]
        except KeyError as exc:
            raise KeyError(f"unknown product id: {product_id}") from exc

    def list_category(self, category: str) -> Tuple[ProductRecord, ...]:
        return tuple(record for record in self._records.values() if record.identity.category == category)
