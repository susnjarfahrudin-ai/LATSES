"""
LAT-CES Module 011: Physical Equation & Formula Engine
Dokument: LAT-SCI-MOD-0011
"""
from typing import Callable
from lat_ces.core.dimensions import Dimension
from lat_ces.modules.quantity import PhysicalQuantity


class PhysicalEquation:
    """Legacy equation facade compatible with canonical PhysicalQuantity values."""

    def __init__(self, name: str, expected_dimension: Dimension, formula: Callable[..., PhysicalQuantity]):
        self.name = name
        self.expected_dimension = expected_dimension
        self.formula = formula

    def compute(self, **kwargs: PhysicalQuantity) -> PhysicalQuantity:
        result = self.formula(**kwargs)
        result_dimension = getattr(result, "dimension", result.unit.dimension)

        if result_dimension != self.expected_dimension:
            raise ValueError(
                f"Greška u jednačini '{self.name}': Očekivana dimenzija {self.expected_dimension}, "
                f"ali je dobijena {result_dimension}!"
            )
        return result
