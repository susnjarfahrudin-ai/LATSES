"""
LAT-CES Module 020: Full Duct Network Integration Simulator v3
Spaja Module 010 do 019 u celovitu mrežnu simulaciju kanala.
"""
from typing import Dict, Any
from lat_ces.core.dimensions import VELOCITY, LENGTH, DENSITY
from lat_ces.scientific.quantities.quantity import PhysicalQuantity
from lat_ces.modules.plenum import PlenumEngine, AREA
from lat_ces.modules.duct import DuctFrictionEngine, VISCOSITY_AIR
from lat_ces.modules.fittings import FittingLossEngine
from lat_ces.modules.pressure import FanEngine, PRESSURE
from lat_ces.modules.psychrometrics import PsychrometricEngine


class DuctNetworkSimulation:
    def __init__(self, max_allowed_pressure_pa: float = 500.0):
        self.plenum_engine = PlenumEngine()
        self.duct_engine = DuctFrictionEngine()
        self.fitting_engine = FittingLossEngine()
        self.fan_engine = FanEngine()
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
        vapor_pressure_pa: float
    ) -> Dict[str, Any]:
        """Izvršava cjelovitu analizu mreže kanala."""
        airflow = self.plenum_engine.calculate_airflow(area, velocity)

        mu = PhysicalQuantity(1.81e-5, VISCOSITY_AIR, 1e-7)
        re = self.duct_engine.calculate_reynolds_number(density, velocity, hydraulic_diameter, mu)
        f = self.duct_engine.estimate_friction_factor(re)
        dp_friction = self.duct_engine.calculate_friction_loss(f, duct_length, hydraulic_diameter, density, velocity)

        dp_fittings = self.fitting_engine.calculate_fitting_loss(fitting_zeta_sum, density, velocity)

        total_dp_val = dp_friction.value + dp_fittings.value
        total_dp = PhysicalQuantity(total_dp_val, PRESSURE, dp_friction.uncertainty + dp_fittings.uncertainty)

        fan_power = self.fan_engine.calculate_fan_power(airflow, total_dp, efficiency=0.8)

        rh = self.psych_engine.calculate_relative_humidity(vapor_pressure_pa, temp_celsius)

        status = "PASS" if total_dp.value <= self.max_allowed_pressure_pa else "FAIL"

        return {
            "airflow": airflow,
            "reynolds": re,
            "dp_friction": dp_friction,
            "dp_fittings": dp_fittings,
            "total_dp": total_dp,
            "fan_power": fan_power,
            "relative_humidity": rh,
            "status": status
        }
