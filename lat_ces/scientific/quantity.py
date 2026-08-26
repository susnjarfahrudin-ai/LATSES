"""Compatibility shim for the canonical scientific quantity package.

The canonical implementation lives in ``lat_ces.scientific.quantity``
(the package directory). This module is kept as a source-level compatibility
entry point and intentionally contains no duplicate PhysicalQuantity logic.
"""

from lat_ces.scientific.quantity import (
    AuditRecord,
    Equation,
    EvidenceLink,
    MeasurementTrace,
    PhysicalQuantity,
    PhysicalQuantityRevisionManager,
    generate_equation_hash,
    generate_quantity_hash,
    verify_quantity_integrity,
)

__all__ = [
    "PhysicalQuantity",
    "MeasurementTrace",
    "EvidenceLink",
    "AuditRecord",
    "PhysicalQuantityRevisionManager",
    "Equation",
    "generate_quantity_hash",
    "generate_equation_hash",
    "verify_quantity_integrity",
]
