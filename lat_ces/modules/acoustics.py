"""LAT-CES Module 013: Acoustic & Noise Engine.

Legacy/domain API retained because the canonical scientific acoustics model
currently covers duct/silencer attenuation rather than this complete helper
surface. It uses only canonical quantity/dimension imports.
"""
import math
from typing import List, Union

from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.core.dimensions import PRESSURE

P_REF = 2e-5


class AcousticsEngine:
    @staticmethod
    def pressure_to_db(pressure_pa: Union[float, PhysicalQuantity]) -> float:
        """Convert acoustic pressure in pascals to sound-pressure level."""
        if isinstance(pressure_pa, PhysicalQuantity):
            if pressure_pa.dimension != PRESSURE:
                raise ValueError(
                    f"Zvučni pritisak mora imati PRESSURE dimenziju, dobijeno: {pressure_pa.dimension}"
                )
            pressure_pa = pressure_pa.value
        if pressure_pa <= 0:
            raise ValueError("Zvučni pritisak mora biti pozitivan!")
        return 20.0 * math.log10(pressure_pa / P_REF)

    @staticmethod
    def combine_noise_levels(levels_db: List[float]) -> float:
        """Combine independent noise sources logarithmically."""
        if not levels_db:
            return 0.0
        sum_linear = sum(10.0 ** (db / 10.0) for db in levels_db)
        return 10.0 * math.log10(sum_linear)

    @staticmethod
    def is_noise_acceptable(total_db: float, max_limit_db: float = 45.0) -> bool:
        return total_db <= max_limit_db
