"""
LAT-CES Module 014: Thermal & Thermodynamic Engine
Dokument: LAT-SCI-MOD-0014

Compatibility adapter over the canonical scientific quantity layer.
"""
from lat_ces.core.dimensions import TEMPERATURE, SPECIFIC_HEAT, HEAT_RATE, MASS_FLOW
from lat_ces.scientific.quantity import Equation, PhysicalQuantity


class ThermalEngine:
    def __init__(self):
        self.heat_rate_equation = Equation(
            "Q_dot = m_dot * cp * delta_T"
        )

    @staticmethod
    def _require_dimension(quantity: PhysicalQuantity, expected, name: str) -> None:
        if quantity.dimension != expected:
            raise ValueError(
                f"{name} must have dimension {expected}, got {quantity.dimension}"
            )

    def calculate_heat_rate(
        self,
        mass_flow: PhysicalQuantity,
        specific_heat: PhysicalQuantity,
        delta_temp: PhysicalQuantity
    ) -> PhysicalQuantity:
        """Računa toplotnu snagu izmjene toplote u zraku (W)."""
        self._require_dimension(mass_flow, MASS_FLOW, "mass_flow")
        self._require_dimension(specific_heat, SPECIFIC_HEAT, "specific_heat")
        self._require_dimension(delta_temp, TEMPERATURE, "delta_temp")

        result = mass_flow * specific_heat * delta_temp
        if result.dimension != HEAT_RATE:
            raise ValueError(
                f"Calculated heat rate has unexpected dimension {result.dimension}"
            )

        return PhysicalQuantity(
            value=result.value,
            uncertainty=result.uncertainty,
            unit=result.unit,
            equation=self.heat_rate_equation,
        )
