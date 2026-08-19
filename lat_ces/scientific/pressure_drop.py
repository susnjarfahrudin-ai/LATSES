"""Canonical pressure-drop model for the LAT-CES fluid stack."""

from __future__ import annotations

from lat_ces.core.dimensions import DENSITY, PRESSURE, VELOCITY
from lat_ces.scientific.quantity import PhysicalQuantity


class PressureError(ValueError):
    """Raised for invalid pressure-drop inputs."""


class PressureDropModel:
    """Compute local pressure loss, ΔP = K ρ v² / 2."""

    def __init__(self, loss_coefficient: float, air_density: float = 1.2):
        if loss_coefficient < 0.0 or air_density <= 0.0:
            raise PressureError("Invalid physical parameters for pressure drop.")
        self.k = float(loss_coefficient)
        self.rho = float(air_density)

    def compute_pressure_drop(self, velocity: float) -> float:
        """Legacy scalar API returning pressure drop in Pa."""
        if velocity < 0.0:
            raise PressureError("Velocity cannot be negative.")
        dp = self.k * self.rho * (velocity ** 2) / 2.0
        return round(dp, 2)

    def compute_quantity_pressure_drop(
        self,
        velocity: PhysicalQuantity,
        density: PhysicalQuantity | None = None,
    ) -> PhysicalQuantity:
        """Canonical quantity-aware pressure-drop API."""
        if velocity.dimension != VELOCITY:
            raise PressureError(
                f"velocity must have dimension {VELOCITY}, got {velocity.dimension}"
            )
        if velocity.value < 0.0:
            raise PressureError("Velocity cannot be negative.")

        if density is None:
            density = PhysicalQuantity(value=self.rho, dimension=DENSITY)
        elif density.dimension != DENSITY:
            raise PressureError(
                f"density must have dimension {DENSITY}, got {density.dimension}"
            )
        if density.value <= 0.0:
            raise PressureError("Density must be positive.")

        value = self.k * density.value * velocity.value ** 2 / 2.0
        relative = (
            (density.uncertainty / density.value) ** 2
            + (2.0 * velocity.uncertainty / velocity.value) ** 2
        ) ** 0.5 if velocity.value else 0.0
        return PhysicalQuantity(
            value=value,
            dimension=PRESSURE,
            uncertainty=abs(value) * relative,
        )


__all__ = ["PressureError", "PressureDropModel"]
