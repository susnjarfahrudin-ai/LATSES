"""Compatibility facade for the canonical PhysicalQuantity engine."""

from __future__ import annotations

from lat_ces.core.dimensions import Unit, UnitSKOError
from lat_ces.scientific.quantities.quantity import PhysicalQuantity
from lat_ces.scientific.units.unit import UnitError


class Quantity(PhysicalQuantity):
    """Legacy constructor and conversion facade backed by canonical PhysicalQuantity."""

    def __init__(self, value: float, unit: Unit, uncertainty: float = 0.0, **kwargs):
        super().__init__(value=value, uncertainty=uncertainty, unit=unit, **kwargs)

    @classmethod
    def _from_result(cls, result: PhysicalQuantity) -> "Quantity":
        return cls(result.value, result.unit, result.uncertainty)

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
        return Quantity(self.value * factor, target_unit, abs(self.uncertainty * factor))

    def __add__(self, other):
        return self._from_result(super().__add__(other))

    def __sub__(self, other):
        return self._from_result(super().__sub__(other))

    def __mul__(self, other):
        result = super().__mul__(other)
        return NotImplemented if result is NotImplemented else self._from_result(result)

    def __truediv__(self, other):
        result = super().__truediv__(other)
        return NotImplemented if result is NotImplemented else self._from_result(result)

    def __pow__(self, exponent):
        result = super().__pow__(exponent)
        return NotImplemented if result is NotImplemented else self._from_result(result)


QuantityError = UnitSKOError

__all__ = ["Quantity", "QuantityError", "Unit", "UnitError"]
