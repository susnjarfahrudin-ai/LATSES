"""
LAT-CES Module 017: Fitting Loss Engine
Dokument: LAT-SCI-MOD-0017
"""
import math
from lat_ces.core.dimensions import DENSITY, VELOCITY
from lat_ces.modules.quantity import PhysicalQuantity
from lat_ces.modules.pressure import PRESSURE

class FittingLossEngine:
    @staticmethod
    def _require_dimension(quantity: PhysicalQuantity, expected, name: str) -> None:
        if quantity.dimension != expected:
            raise ValueError(
                f"{name} must have dimension {expected}, got {quantity.dimension}"
            )

    @classmethod
    def calculate_fitting_loss(
        cls,
        zeta: float,
        density: PhysicalQuantity,
        velocity: PhysicalQuantity
    ) -> PhysicalQuantity:
        """
        Računa lokalni pad pritiska na fitingu: delta_P = zeta * (rho * v^2 / 2)
        """
        if zeta < 0:
            raise ValueError("Koeficijent otpora (zeta) ne može biti negativan!")

        cls._require_dimension(density, DENSITY, "density")
        cls._require_dimension(velocity, VELOCITY, "velocity")

        dp_val = zeta * (density.value * (velocity.value ** 2) / 2.0)

        u_rel = math.sqrt(
            (density.uncertainty / density.value)**2 +
            (2.0 * velocity.uncertainty / velocity.value)**2
        )

        return PhysicalQuantity(
            value=dp_val,
            dimension=PRESSURE,
            uncertainty=dp_val * u_rel
        )
