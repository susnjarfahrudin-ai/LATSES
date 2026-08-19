"""Compatibility facade for the legacy duct-friction module.

Canonical duct-friction execution lives in ``lat_ces.scientific.duct_friction``.
This module preserves the legacy ``DuctFrictionEngine`` API while delegating
all scientific calculations to the canonical model.
"""

from lat_ces.core.dimensions import DYNAMIC_VISCOSITY
from lat_ces.scientific.duct_friction import DuctError, DuctFrictionModel

VISCOSITY_AIR = DYNAMIC_VISCOSITY


class DuctFrictionEngine:
    """Legacy adapter around the canonical :class:`DuctFrictionModel`."""

    def __init__(self, friction_factor: float = 0.02):
        self._model = DuctFrictionModel(friction_factor=friction_factor)

    @classmethod
    def calculate_reynolds_number(cls, density, velocity, hydraulic_diameter, dynamic_viscosity):
        return DuctFrictionModel.calculate_reynolds_number(
            density, velocity, hydraulic_diameter, dynamic_viscosity
        )

    @staticmethod
    def estimate_friction_factor(reynolds: float) -> float:
        return DuctFrictionModel.estimate_friction_factor(reynolds)

    def calculate_friction_loss(
        self,
        friction_factor,
        length,
        hydraulic_diameter,
        density,
        velocity,
    ):
        # Preserve the historical API where friction_factor is supplied per call.
        return DuctFrictionModel(friction_factor=friction_factor).compute_quantity_friction_loss(
            length=length,
            hydraulic_diameter=hydraulic_diameter,
            density=density,
            velocity=velocity,
        )


__all__ = ["DuctError", "DuctFrictionEngine", "VISCOSITY_AIR"]
