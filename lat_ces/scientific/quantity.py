"""Canonical physical Quantity built on the existing Unit/Dimension system."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real
from typing import Any

from lat_ces.scientific.units.core import Unit, convert_unit


class QuantityError(ValueError):
    """Raised when a Quantity operation is physically invalid."""


@dataclass(frozen=True)
class Quantity:
    """A numerical value bound to one canonical Unit."""

    value: Real
    unit: Unit
    provenance: Any = None
    uncertainty_ref: Any = None

    def __post_init__(self) -> None:
        if not isinstance(self.value, Real):
            raise TypeError("Quantity.value must be a real numeric value")
        if not isinstance(self.unit, Unit):
            raise TypeError("Quantity.unit must use the canonical Unit type")

    @property
    def dimension(self):
        return self.unit.dimension

    def to(self, target: Unit) -> "Quantity":
        if not isinstance(target, Unit):
            raise TypeError("target must be a Unit")
        return Quantity(convert_unit(self.value, self.unit, target), target, self.provenance, self.uncertainty_ref)

    def _compatible(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity):
            raise TypeError("Operation requires another Quantity")
        if self.dimension != other.dimension:
            raise QuantityError(f"Dimension mismatch: {self.dimension!r} != {other.dimension!r}")
        return other.to(self.unit)

    def __add__(self, other: "Quantity") -> "Quantity":
        other = self._compatible(other)
        return Quantity(self.value + other.value, self.unit, self.provenance, self.uncertainty_ref)

    def __sub__(self, other: "Quantity") -> "Quantity":
        other = self._compatible(other)
        return Quantity(self.value - other.value, self.unit, self.provenance, self.uncertainty_ref)

    def __mul__(self, other: Any) -> "Quantity":
        if isinstance(other, Quantity):
            return Quantity(self.value * other.value, self.unit * other.unit, self.provenance, self.uncertainty_ref)
        if isinstance(other, Real):
            return Quantity(self.value * other, self.unit, self.provenance, self.uncertainty_ref)
        return NotImplemented

    def __rmul__(self, other: Any) -> "Quantity":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "Quantity":
        if isinstance(other, Quantity):
            if other.value == 0:
                raise ZeroDivisionError("Cannot divide by a zero Quantity")
            return Quantity(self.value / other.value, self.unit / other.unit, self.provenance, self.uncertainty_ref)
        if isinstance(other, Real):
            if other == 0:
                raise ZeroDivisionError("Cannot divide Quantity by zero")
            return Quantity(self.value / other, self.unit, self.provenance, self.uncertainty_ref)
        return NotImplemented

    def __pow__(self, power: int | float) -> "Quantity":
        if not isinstance(power, Real):
            raise TypeError("Quantity exponent must be numeric")
        return Quantity(self.value**power, self.unit**power, self.provenance, self.uncertainty_ref)

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.unit, self.provenance, self.uncertainty_ref)

    def __repr__(self) -> str:
        return f"Quantity(value={self.value!r}, unit={self.unit.symbol!r})"


__all__ = ["Quantity", "QuantityError"]
