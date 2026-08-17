"""Compatibility implementation for the legacy SCI-0011 PhysicalEquation API.

The implementation lives under the canonical Scientific Equations namespace so
legacy callers can migrate without maintaining a second equation engine.
"""

from __future__ import annotations

from typing import Callable

from lat_ces.core.dimensions import Dimension
from lat_ces.scientific.quantity.quantity import PhysicalQuantity
from lat_ces.scientific.quantity.equation import Equation


class PhysicalEquation:
    """Legacy SCI-0011 equation API backed by the canonical Scientific Quantity."""

    def __init__(
        self,
        name: str,
        expected_dimension: Dimension,
        formula: Callable[..., PhysicalQuantity],
    ) -> None:
        self.equation = Equation(name)
        self.name = self.equation.expression
        self.expected_dimension = expected_dimension
        self.formula = formula

    def compute(self, **kwargs: PhysicalQuantity) -> PhysicalQuantity:
        result = self.formula(**kwargs)
        if result.dimension != self.expected_dimension:
            raise ValueError(
                f"Greška u jednačini '{self.equation.expression}': "
                f"Očekivana dimenzija {self.expected_dimension}, "
                f"ali je dobijena {result.dimension}!"
            )
        return result


__all__ = ["PhysicalEquation"]
