"""Canonical fluid-mechanics fitting-loss model.

The legacy ``lat_ces.modules.fittings`` namespace is retained only as a
compatibility facade.  Physics belongs in this scientific layer.
"""

import math

from lat_ces.core.dimensions import DENSITY, PRESSURE, VELOCITY
from lat_ces.scientific.quantity import PhysicalQuantity


class FittingLossError(ValueError):
    """Raised for invalid fitting-loss inputs."""


class FittingLossModel:
    """Computes local fitting pressure loss, ΔP = ζρv²/2."""

    @staticmethod
    def _require_dimension(quantity: PhysicalQuantity, expected, name: str) -> None:
        if quantity.dimension != expected:
            raise FittingLossError(
                f"{name} must have dimension {expected}, got {quantity.dimension}"
            )

    @classmethod
    def compute_pressure_loss(
        cls,
        zeta: float,
        density: PhysicalQuantity,
        velocity: PhysicalQuantity,
    ) -> PhysicalQuantity:
        if zeta < 0:
            raise FittingLossError("Loss coefficient zeta cannot be negative.")
        cls._require_dimension(density, DENSITY, "density")
        cls._require_dimension(velocity, VELOCITY, "velocity")
        if density.value <= 0 or velocity.value < 0:
            raise FittingLossError("Density must be positive and velocity non-negative.")
        value = zeta * density.value * velocity.value**2 / 2.0
        u_rel = math.sqrt(
            (density.uncertainty / density.value) ** 2
            + (2.0 * velocity.uncertainty / velocity.value) ** 2
        ) if velocity.value else 0.0
        return PhysicalQuantity(value=value, dimension=PRESSURE, uncertainty=value * u_rel)


__all__ = ["FittingLossError", "FittingLossModel"]
