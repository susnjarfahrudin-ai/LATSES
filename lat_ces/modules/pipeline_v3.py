"""
LAT-CES Module 020: Full Duct Network Integration Simulator v3
Spaja Module 010 do 019 u celovitu mrežnu simulaciju kanala.

Legacy module retained as an integration facade; fluid-mechanics calculations
are delegated directly to canonical scientific models.
"""
from typing import Any, Dict

from lat_ces.core.dimensions import AREA, DENSITY, DYNAMIC_VISCOSITY, LENGTH, VELOCITY
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.scientific.plenum import PlenumEngine
from lat_ces.scientific.duct_friction import DuctFrictionModel
from lat_ces.scientific.fittings import FittingLossModel
from lat_ces.scientific.fan_power import FanPowerModel
from lat_ces.modules.psychrometrics import PsychrometricEngine


class DuctNetworkSimulation:
    """Module-020 compatibility facade using canonical fluid scientific models."""

    def __init__(self, max_allowed_pressure_pa: float = 500.0):
        self.plenum_engine = PlenumEngine()
        self.duct_model = DuctFrictionModel()
        self.fitting_model = FittingLossModel()
        self.psych_engine = PsychrometricEngine()
        self.max_allowed_pressure_pa = max_allowed_pressure_pa

    def run_network_simulation(
        self,
        area: PhysicalQuantity,
        velocity: PhysicalQuantity,
        density: PhysicalQuantity,
        duct_length: PhysicalQuantity,
        hydraulic_diameter: PhysicalQuantity,
        fitting_zeta_sum: float,
        temp_celsius: float,
        vapor_pressure_pa: float,
    ) -> Dict[str, Any]:
        """Izvršava cjelovitu analizu mreže kanala."""
        if area.dimension != AREA:
            raise ValueError(f"area must have dimension {AREA}, got {area.dimension}")
        if velocity.dimension != VELOCITY:
            raise ValueError(
                f"velocity must have dimension {VELOCITY}, got {velocity.dimension}"
            )
        if density.dimension != DENSITY:
            raise ValueError(
                f"density must have dimension {DENSITY}, got {density.dimension}"
            )
        if duct_length.dimension != LENGTH:
            raise ValueError(
                f"duct_length must have dimension {LENGTH}, got {duct_length.dimension}"
            )
        if hydraulic_diameter.dimension != LENGTH:
            raise ValueError(
                f"hydraulic_diameter must have dimension {LENGTH}, got {hydraulic_diameter.dimension}"
            )

        airflow = self.plenum_engine.calculate_airflow(area, velocity)

        dynamic_viscosity = PhysicalQuantity(
            1.81e-5,
            dimension=DYNAMIC_VISCOSITY,
            uncertainty=1e-7,
        )
        reynolds = self.duct_model.calculate_reynolds_number(
            density,
            velocity,
            hydraulic_diameter,
            dynamic_viscosity,
        )
        friction_factor = self.duct_model.estimate_friction_factor(reynolds)
        duct_model = DuctFrictionModel(friction_factor=friction_factor)
        dp_friction = duct_model.compute_quantity_friction_loss(
            duct_length,
            hydraulic_diameter,
            density,
            velocity,
        )

        dp_fittings = self.fitting_model.compute_pressure_loss(
            fitting_zeta_sum,
            density,
            velocity,
        )

        total_dp_value = dp_friction.value + dp_fittings.value
        total_dp_uncertainty = dp_friction.uncertainty + dp_fittings.uncertainty
        total_dp = PhysicalQuantity(
            total_dp_value,
            dimension=dp_friction.dimension,
            uncertainty=total_dp_uncertainty,
        )

        fan_power = FanPowerModel.calculate(
            airflow,
            total_dp,
            efficiency=0.8,
        )

        rh = self.psych_engine.calculate_relative_humidity(
            vapor_pressure_pa,
            temp_celsius,
        )

        status = "PASS" if total_dp.value <= self.max_allowed_pressure_pa else "FAIL"

        return {
            "airflow": airflow,
            "reynolds": reynolds,
            "dp_friction": dp_friction,
            "dp_fittings": dp_fittings,
            "total_dp": total_dp,
            "fan_power": fan_power,
            "relative_humidity": rh,
            "status": status,
        }
