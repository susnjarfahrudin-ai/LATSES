"""
LAT-CES Scientific Core
Quantity Engine Reference Implementation Rev A
Princip: Value + Unit -> PhysicalQuantity
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional, Union

from lat_ces.scientific.units.units import Unit, UnitSKOError


@dataclass(init=False)
class PhysicalQuantity:
    """
    Represents a physical quantity consisting of a numerical value and a unit.
    Provides safe arithmetic operations with automatic dimensional consistency.
    """

    value: float
    unit: Unit
    uncertainty: float = 0.0

    def __init__(
        self,
        value: float,
        unit_or_uncertainty: Union[Unit, float],
        maybe_unit: Optional[Unit] = None,
    ):
        # Rev A form: PhysicalQuantity(value, unit)
        if maybe_unit is None:
            if not hasattr(unit_or_uncertainty, "dimension") or not hasattr(
                unit_or_uncertainty, "scale_factor"
            ):
                raise UnitSKOError("Skraćeni oblik zahtijeva PhysicalQuantity(value, unit).")
            self.value = float(value)
            self.unit = unit_or_uncertainty
            self.uncertainty = 0.0
            return

        # Backward-compatible form: PhysicalQuantity(value, uncertainty, unit)
        uncertainty = float(unit_or_uncertainty)
        if uncertainty < 0.0:
            raise UnitSKOError("Mjerna neodređenost ne može biti negativna vrijednost.")

        self.value = float(value)
        self.unit = maybe_unit
        self.uncertainty = uncertainty

    @property
    def dimension(self):
        return self.unit.dimension

    @property
    def relative_uncertainty(self) -> float:
        if self.value == 0.0:
            return 0.0 if self.uncertainty == 0.0 else float("inf")
        return abs(self.uncertainty / self.value)

    def __add__(self, other: "PhysicalQuantity") -> "PhysicalQuantity":
        if self.unit.dimension != other.unit.dimension:
            raise UnitSKOError(
                f"Dimenzionalna neslaganja: {self.unit.dimension} vs {other.unit.dimension}"
            )

        other_converted_val = (other.value * other.unit.scale_factor) / self.unit.scale_factor
        other_converted_unc = (other.uncertainty * other.unit.scale_factor) / self.unit.scale_factor

        new_val = self.value + other_converted_val
        new_unc = math.sqrt(self.uncertainty**2 + other_converted_unc**2)

        return PhysicalQuantity(new_val, new_unc, self.unit)

    def __sub__(self, other: "PhysicalQuantity") -> "PhysicalQuantity":
        if self.unit.dimension != other.unit.dimension:
            raise UnitSKOError(
                f"Dimenzionalna neslaganja: {self.unit.dimension} vs {other.unit.dimension}"
            )

        other_converted_val = (other.value * other.unit.scale_factor) / self.unit.scale_factor
        other_converted_unc = (other.uncertainty * other.unit.scale_factor) / self.unit.scale_factor

        new_val = self.value - other_converted_val
        new_unc = math.sqrt(self.uncertainty**2 + other_converted_unc**2)

        return PhysicalQuantity(new_val, new_unc, self.unit)

    def __mul__(self, other: Union["PhysicalQuantity", int, float]) -> "PhysicalQuantity":
        if isinstance(other, PhysicalQuantity):
            new_val = self.value * other.value
            new_unit = self.unit * other.unit
            rel_unc_sq = self.relative_uncertainty**2 + other.relative_uncertainty**2
            new_unc = abs(new_val) * math.sqrt(rel_unc_sq)
            return PhysicalQuantity(new_val, new_unc, new_unit)

        if isinstance(other, (int, float)):
            scalar = float(other)
            return PhysicalQuantity(self.value * scalar, self.uncertainty * abs(scalar), self.unit)

        return NotImplemented

    def __rmul__(self, other: Union[int, float]) -> "PhysicalQuantity":
        return self.__mul__(other)

    def __truediv__(self, other: Union["PhysicalQuantity", int, float]) -> "PhysicalQuantity":
        if isinstance(other, PhysicalQuantity):
            if other.value == 0.0:
                raise ZeroDivisionError(
                    "Dijeljenje sa fizikalnom veličinom čija je vrijednost 0.0 nije dozvoljeno."
                )

            new_val = self.value / other.value
            new_unit = self.unit / other.unit
            rel_unc_sq = self.relative_uncertainty**2 + other.relative_uncertainty**2
            new_unc = abs(new_val) * math.sqrt(rel_unc_sq)
            return PhysicalQuantity(new_val, new_unc, new_unit)

        if isinstance(other, (int, float)):
            if other == 0.0:
                raise ZeroDivisionError("Dijeljenje sa skalarom 0 nije dozvoljeno.")
            return PhysicalQuantity(
                self.value / other,
                self.uncertainty / abs(other),
                self.unit,
            )

        return NotImplemented

    def __rtruediv__(self, other: Union[int, float]) -> "PhysicalQuantity":
        if isinstance(other, (int, float)):
            if self.value == 0.0:
                raise ZeroDivisionError("Dijeljenje skalara sa nulom nije dozvoljeno.")

            scalar = float(other)
            new_val = scalar / self.value
            new_unit = self.unit ** -1
            new_unc = abs(new_val) * self.relative_uncertainty
            return PhysicalQuantity(new_val, new_unc, new_unit)

        return NotImplemented

    def __pow__(self, exponent: Union[int, float]) -> "PhysicalQuantity":
        if not isinstance(exponent, (int, float)):
            return NotImplemented

        exp = float(exponent)
        new_val = self.value ** exp
        new_unit = self.unit ** exp
        new_unc = abs(new_val) * abs(exp) * self.relative_uncertainty
        return PhysicalQuantity(new_val, new_unc, new_unit)

    def sqrt(self) -> "PhysicalQuantity":
        """Return the square root of this physical quantity."""
        return self ** 0.5

    def __repr__(self) -> str:
        return (
            f"{self.value:.4f} ± {self.uncertainty:.4f} {self.unit.symbol} "
            f"(u_rel: {self.relative_uncertainty * 100:.2f}%)"
        )
