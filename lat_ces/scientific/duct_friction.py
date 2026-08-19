"""Canonical Darcy-Weisbach duct-friction model for the LAT-CES fluid stack."""

from __future__ import annotations

from lat_ces.core.dimensions import DENSITY, DYNAMIC_VISCOSITY, LENGTH, PRESSURE, VELOCITY
from lat_ces.scientific.quantity import PhysicalQuantity


class DuctError(ValueError):
    """Raised for invalid duct-friction inputs."""


class DuctFrictionModel:
    """Canonical Reynolds, friction-factor, and Darcy-Weisbach pressure-loss model."""

    def __init__(self, friction_factor: float = 0.02):
        if friction_factor <= 0.0:
            raise DuctError("Friction factor must be positive.")
        self.friction_factor = float(friction_factor)

    @staticmethod
    def _require_dimension(quantity: PhysicalQuantity, expected, name: str) -> None:
        if quantity.dimension != expected:
            raise DuctError(
                f"{name} must have dimension {expected}, got {quantity.dimension}"
            )

    @classmethod
    def calculate_reynolds_number(
        cls,
        density: PhysicalQuantity,
        velocity: PhysicalQuantity,
        hydraulic_diameter: PhysicalQuantity,
        dynamic_viscosity: PhysicalQuantity,
    ) -> float:
        cls._require_dimension(density, DENSITY, "density")
        cls._require_dimension(velocity, VELOCITY, "velocity")
        cls._require_dimension(hydraulic_diameter, LENGTH, "hydraulic_diameter")
        cls._require_dimension(dynamic_viscosity, DYNAMIC_VISCOSITY, "dynamic_viscosity")
        if density.value <= 0.0:
            raise DuctError("Density must be positive.")
        if dynamic_viscosity.value <= 0.0:
            raise DuctError("Dynamic viscosity must be positive.")
        if velocity.value < 0.0:
            raise DuctError("Velocity cannot be negative.")
        if hydraulic_diameter.value <= 0.0:
            raise DuctError("Hydraulic diameter must be positive.")
        return (
            density.value * velocity.value * hydraulic_diameter.value
        ) / dynamic_viscosity.value

    @staticmethod
    def estimate_friction_factor(reynolds: float) -> float:
        if reynolds <= 0.0:
            raise DuctError("Reynolds number must be positive.")
        if reynolds < 2300.0:
            return 64.0 / reynolds
        return 0.3164 / (reynolds ** 0.25)

    def compute_friction_loss(
        self,
        length_m: float,
        diameter_m: float,
        velocity_m_s: float,
        air_density: float = 1.2,
    ) -> float:
        """Compute straight-duct pressure loss in Pa: Δp=f(L/D)(ρv²/2)."""
        if length_m < 0.0 or diameter_m <= 0.0 or velocity_m_s < 0.0:
            raise DuctError("Length, diameter, and velocity must be physically valid.")
        if air_density <= 0.0:
            raise DuctError("Air density must be positive.")

        dynamic_pressure = 0.5 * air_density * (velocity_m_s ** 2)
        pressure_loss = self.friction_factor * (length_m / diameter_m) * dynamic_pressure
        return round(pressure_loss, 2)

    def compute_quantity_friction_loss(
        self,
        length: PhysicalQuantity,
        hydraulic_diameter: PhysicalQuantity,
        density: PhysicalQuantity,
        velocity: PhysicalQuantity,
    ) -> PhysicalQuantity:
        """Quantity-aware Darcy-Weisbach pressure loss with uncertainty propagation."""
        self._require_dimension(length, LENGTH, "length")
        self._require_dimension(hydraulic_diameter, LENGTH, "hydraulic_diameter")
        self._require_dimension(density, DENSITY, "density")
        self._require_dimension(velocity, VELOCITY, "velocity")
        if length.value < 0.0:
            raise DuctError("Length cannot be negative.")
        if hydraulic_diameter.value <= 0.0:
            raise DuctError("Hydraulic diameter must be positive.")
        if density.value <= 0.0:
            raise DuctError("Density must be positive.")
        if velocity.value < 0.0:
            raise DuctError("Velocity cannot be negative.")

        value = self.compute_friction_loss(
            length_m=length.value,
            diameter_m=hydraulic_diameter.value,
            velocity_m_s=velocity.value,
            air_density=density.value,
        )

        def relative_uncertainty(quantity: PhysicalQuantity) -> float:
            if quantity.value == 0.0:
                return 0.0 if quantity.uncertainty == 0.0 else float("inf")
            return abs(quantity.uncertainty / quantity.value)

        rel = (
            relative_uncertainty(length) ** 2
            + relative_uncertainty(hydraulic_diameter) ** 2
            + relative_uncertainty(density) ** 2
            + (2.0 * relative_uncertainty(velocity)) ** 2
        ) ** 0.5

        return PhysicalQuantity(
            value=value,
            dimension=PRESSURE,
            uncertainty=abs(value) * rel,
        )


__all__ = ["DuctError", "DuctFrictionModel"]
