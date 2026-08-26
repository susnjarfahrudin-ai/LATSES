"""LAT-CES Scientific Physical Quantity hardening layer (SCI 42-45)."""

from .audit import AuditRecord
from .quantity import EvidenceLink, MeasurementTrace, PhysicalQuantity, PhysicalQuantityRevisionManager
from .equation import Equation
from .integrity import generate_equation_hash, generate_quantity_hash, verify_quantity_integrity
from .strict import Quantity, QuantityError

__all__ = [
    "PhysicalQuantity",
    "Quantity",
    "QuantityError",
    "MeasurementTrace",
    "EvidenceLink",
    "AuditRecord",
    "PhysicalQuantityRevisionManager",
    "Equation",
    "generate_quantity_hash",
    "generate_equation_hash",
    "verify_quantity_integrity",
]
