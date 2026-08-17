"""
LAT-CES System Integration & Simulation Engine v2
Spaja Module 010-015 u jedinstvenu sveobuhvatnu simulaciju plenum sistema.
"""
from typing import Dict, Any
from lat_ces.core.dimensions import Dimension
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import PlenumEngine
from lat_ces.modules.acoustics import AcousticsEngine
from lat_ces.modules.thermal import ThermalEngine
from lat_ces.modules.pressure import FanEngine

class FullPlenumSimulation:
    def __init__(self, max_allowed_noise_db: float = 45.0, fan_efficiency: float = 0.8):
        self.plenum_engine = PlenumEngine()
        self.acoustics_engine = AcousticsEngine()
        self.thermal_engine = ThermalEngine()
        self.fan_engine = FanEngine()
        self.max_allowed_noise_db = max_allowed_noise_db
        self.fan_efficiency = fan_efficiency

    def run_full_simulation(
        self,
        area: PhysicalQuantity,
        velocity: PhysicalQuantity,
        density: PhysicalQuantity,
        sound_pressure_pa: float,
        specific_heat: PhysicalQuantity,
        delta_temp: PhysicalQuantity,
        pressure_drop: PhysicalQuantity
    ) -> Dict[str, Any]:
        """Izvršava cjelovitu fizikalno-inženjersku simulaciju plenuma."""
        airflow = self.plenum_engine.calculate_airflow(area, velocity)
        mass_flow = self.plenum_engine.calculate_mass_flow(density, airflow)

        noise_db = self.acoustics_engine.pressure_to_db(sound_pressure_pa)
        is_noise_ok = self.acoustics_engine.is_noise_acceptable(noise_db, self.max_allowed_noise_db)

        heat_rate = self.thermal_engine.calculate_heat_rate(mass_flow, specific_heat, delta_temp)

        fan_power = self.fan_engine.calculate_fan_power(airflow, pressure_drop, self.fan_efficiency)

        status = "PASS" if is_noise_ok else "FAIL"

        return {
            "airflow": airflow,
            "mass_flow": mass_flow,
            "noise_db": noise_db,
            "noise_acceptable": is_noise_ok,
            "heat_rate": heat_rate,
            "fan_power": fan_power,
            "status": status
        }


class PlenumSystemSimulation(FullPlenumSimulation):
    def run_simulation(
        self,
        area: PhysicalQuantity,
        velocity: PhysicalQuantity,
        density: PhysicalQuantity,
        sound_pressure_pa: float
    ) -> Dict[str, Any]:
        """Backward-compatible wrapper for the older pipeline interface."""
        airflow = self.plenum_engine.calculate_airflow(area, velocity)
        mass_flow = self.plenum_engine.calculate_mass_flow(density, airflow)

        noise_db = self.acoustics_engine.pressure_to_db(sound_pressure_pa)
        is_noise_ok = self.acoustics_engine.is_noise_acceptable(noise_db, self.max_allowed_noise_db)

        return {
            "airflow": airflow,
            "mass_flow": mass_flow,
            "noise_db": noise_db,
            "noise_acceptable": is_noise_ok,
            "status": "PASS" if is_noise_ok else "FAIL",
        }