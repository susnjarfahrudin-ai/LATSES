"""Read-only access to manufacturer-declared technical product data."""

from .reader import TechnicalCatalog, TechnicalProductRecord
from .models import ProductIdentity, ProductProperty, ProductRecord, ProductRegistry
from .standards import StandardReference, StandardsRegistry

__all__ = [
    "TechnicalCatalog",
    "TechnicalProductRecord",
    "ProductIdentity",
    "ProductProperty",
    "ProductRecord",
    "ProductRegistry",
    "StandardReference",
    "StandardsRegistry",
]
