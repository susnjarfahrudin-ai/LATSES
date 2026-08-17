"""Compatibility facade for the canonical fitting-loss model."""

from lat_ces.core.dimensions import DENSITY, PRESSURE, VELOCITY
from lat_ces.scientific.fittings import FittingLossError, FittingLossModel
from lat_ces.scientific.quantity import PhysicalQuantity


class FittingLossEngine:
    """Backward-compatible API delegating all physics to the canonical model."""

    @staticmethod
    def calculate_fitting_loss(
        zeta: float,
        density: PhysicalQuantity,
        velocity: PhysicalQuantity,
    ) -> PhysicalQuantity:
        return FittingLossModel.compute_pressure_loss(zeta, density, velocity)


__all__ = ["FittingLossEngine", "FittingLossError", "FittingLossModel"]
