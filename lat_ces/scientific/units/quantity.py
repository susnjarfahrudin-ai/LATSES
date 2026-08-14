"""Compatibility facade for the canonical PhysicalQuantity engine."""

from __future__ import annotations

from lat_ces.core.dimensions import Unit, UnitSKOError
from lat_ces.scientific.quantities.quantity import PhysicalQuantity
from lat_ces.scientific.units.unit import UnitError


class Quantity(PhysicalQuantity):
    """Legacy constructor and conversion facade backed by canonical PhysicalQuantity."""

    def __init__(self, value: float, unit: Unit, uncertainty: float = 0.0, **kwargs):
        super().__init__(value=value, uncertainty=uncertainty, unit=unit, **kwargs)

    def to(self, target_unit: Unit) -> "Quantity":
        if not isinstance(target_unit, Unit):
            raise QuantityError("Target must be a valid Unit instance.")
        if not self.unit.is_compatible(target_unit):
            raise QuantityError(
                f"Cannot convert incompatible dimensions: {self.dimension} and {target_unit.dimension}"
            )
        if self.unit.offset != 0.0 or target_unit.offset != 0.0:
            raise QuantityError("Affine unit conversion requires the canonical convert_unit API.")
        factor = self.unit.get_conversion_factor_to(target_unit)
        return Quantity(
            value=self.value * factor,
            unit=target_unit,
            uncertainty=abs(self.uncertainty * factor),
        )


QuantityError = UnitSKOError

__all__ = ["Quantity", "QuantityError", "Unit", "UnitError"]
