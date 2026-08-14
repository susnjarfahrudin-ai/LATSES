"""Compatibility facade for the canonical PhysicalQuantity engine."""

from __future__ import annotations

from lat_ces.core.dimensions import Unit, UnitSKOError
from lat_ces.scientific.quantities.quantity import PhysicalQuantity
from lat_ces.scientific.units.unit import UnitError


class Quantity(PhysicalQuantity):
    """Legacy constructor facade backed by canonical PhysicalQuantity."""

    def __init__(self, value: float, unit: Unit, uncertainty: float = 0.0, **kwargs):
        super().__init__(value=value, uncertainty=uncertainty, unit=unit, **kwargs)


class QuantityError(UnitSKOError):
    """Legacy exception name retained for compatibility."""


__all__ = ["Quantity", "QuantityError", "Unit", "UnitError"]
