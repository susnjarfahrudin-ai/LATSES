"""Compatibility facade for the canonical PhysicalQuantity engine.

The original Module 010 API accepted ``(value, dimension, uncertainty)``.
This facade preserves that constructor while storing the quantity in the
scientific PhysicalQuantity engine backed by the canonical Unit model.
"""

from __future__ import annotations

from lat_ces.core.dimensions import Dimension, Unit
from lat_ces.scientific.quantities.quantity import PhysicalQuantity as _CanonicalPhysicalQuantity


def _unit_for_dimension(dimension: Dimension) -> Unit:
    """Create a zero-offset compatibility unit for a dimension-only legacy value."""
    symbol = (
        f"L{dimension.L}M{dimension.M}T{dimension.T}"
        f"I{dimension.I}Th{dimension.Theta}N{dimension.N}J{dimension.J}"
    )
    return Unit(
        name=f"legacy-dimension:{symbol}",
        symbol=symbol,
        dimension=dimension,
        scale_factor=1.0,
        offset=0.0,
    )


class PhysicalQuantity(_CanonicalPhysicalQuantity):
    """Legacy Module 010 constructor backed by canonical PhysicalQuantity."""

    def __init__(self, value: float, dimension=None, uncertainty: float = 0.0, *, unit: Unit | None = None, **kwargs):
        if unit is None:
            if not isinstance(dimension, Dimension):
                raise TypeError("Legacy PhysicalQuantity requires a Dimension or an explicit Unit.")
            unit = _unit_for_dimension(dimension)
        super().__init__(value=value, uncertainty=uncertainty, unit=unit, **kwargs)

    @staticmethod
    def _wrap(result: _CanonicalPhysicalQuantity) -> "PhysicalQuantity":
        return PhysicalQuantity(result.value, unit=result.unit, uncertainty=result.uncertainty)

    def __add__(self, other):
        return self._wrap(super().__add__(other))

    def __sub__(self, other):
        return self._wrap(super().__sub__(other))

    def __mul__(self, other):
        result = super().__mul__(other)
        return NotImplemented if result is NotImplemented else self._wrap(result)

    def __truediv__(self, other):
        result = super().__truediv__(other)
        return NotImplemented if result is NotImplemented else self._wrap(result)

    def __rtruediv__(self, other):
        result = super().__rtruediv__(other)
        return NotImplemented if result is NotImplemented else self._wrap(result)

    def __pow__(self, exponent):
        result = super().__pow__(exponent)
        return NotImplemented if result is NotImplemented else self._wrap(result)


__all__ = ["PhysicalQuantity"]
