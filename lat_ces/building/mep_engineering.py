"""Engineering integration for BuildingModel-owned MEP objects."""
from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Any

from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch
from lat_ces.core.dimensions import DENSITY, DYNAMIC_VISCOSITY, LENGTH, VELOCITY
from lat_ces.scientific.duct_friction import DuctFrictionModel
from lat_ces.scientific.pressure_drop import PressureDropModel
from lat_ces.scientific.quantity import PhysicalQuantity


@dataclass(frozen=True)
class EngineeringResult:
    object_type: str
    object_id: str
    status: str
    values: dict[str, Any]
    message: str = ""


class EngineeringResultRegistry:
    def __init__(self) -> None:
        self._results: dict[tuple[str, str], EngineeringResult] = {}

    def put(self, result: EngineeringResult) -> EngineeringResult:
        self._results[(result.object_type, result.object_id)] = result
        return result

    def get(self, object_type: str, object_id: str) -> EngineeringResult | None:
        return self._results.get((object_type, object_id))

    def remove(self, object_type: str, object_id: str) -> EngineeringResult | None:
        return self._results.pop((object_type, object_id), None)

    @property
    def all(self) -> tuple[EngineeringResult, ...]:
        return tuple(self._results.values())

    @property
    def mep_findings(self) -> tuple[str, ...]:
        """Compatibility view for GUI consumers of the pre-registry findings API."""
        return tuple(
            f"{result.object_type}: {result.status} — {result.message}"
            for result in self._results.values()
        )


def ensure_engineering_results(registry: object) -> EngineeringResultRegistry:
    results = getattr(registry, "engineering_results", None)
    if results is None:
        results = EngineeringResultRegistry()
        setattr(registry, "engineering_results", results)
    if not isinstance(results, EngineeringResultRegistry):
        raise TypeError("BuildingModel.mep.engineering_results must be an EngineeringResultRegistry")
    return results


class MEPEngineeringService:
    WATER_CP_J_KG_K = 4180.0
    HEATING_INPUT_REL_TOL = 0.01

    def __init__(self, *, water_density_kg_m3: float = 998.2, water_dynamic_viscosity_pa_s: float = 1.002e-3) -> None:
        if water_density_kg_m3 <= 0.0 or water_dynamic_viscosity_pa_s <= 0.0:
            raise ValueError("Water density and dynamic viscosity must be positive")
        self.water_density = water_density_kg_m3
        self.water_viscosity = water_dynamic_viscosity_pa_s

    def calculate_ventilation(self, opening: VentilationOpening) -> EngineeringResult:
        area = opening.area_m2
        velocity = opening.design_velocity_m_s
        pressure = PressureDropModel(loss_coefficient=1.0, air_density=1.2).compute_pressure_drop(velocity)
        return EngineeringResult("ventilation", opening.id, "CALCULATED", {
            "area_m2": area,
            "design_flow_m3_s": opening.design_flow_m3_s,
            "design_flow_m3_h": opening.design_flow_m3_h,
            "design_velocity_m_s": velocity,
            "reference_local_pressure_drop_pa": pressure,
        }, "Ventilation opening evaluated with the canonical pressure-drop model.")

    def calculate_water(self, branch: WaterBranch) -> EngineeringResult:
        area = pi * branch.diameter_m**2 / 4.0
        velocity = branch.design_flow_m3_s / area if area > 0.0 else 0.0
        if velocity == 0.0:
            return EngineeringResult("water", branch.id, "INPUT_REQUIRED", {"cross_section_m2": area, "velocity_m_s": 0.0}, "Design flow must be greater than zero for hydraulic evaluation.")
        density = PhysicalQuantity(self.water_density, dimension=DENSITY)
        velocity_q = PhysicalQuantity(velocity, dimension=VELOCITY)
        diameter_q = PhysicalQuantity(branch.diameter_m, dimension=LENGTH)
        viscosity_q = PhysicalQuantity(self.water_viscosity, dimension=DYNAMIC_VISCOSITY)
        reynolds = DuctFrictionModel.calculate_reynolds_number(density, velocity_q, diameter_q, viscosity_q)
        friction_factor = DuctFrictionModel.estimate_friction_factor(reynolds)
        pressure_drop = DuctFrictionModel(friction_factor=friction_factor).compute_friction_loss(
            length_m=branch.length_m, diameter_m=branch.diameter_m, velocity_m_s=velocity, air_density=self.water_density
        )
        return EngineeringResult("water", branch.id, "CALCULATED", {
            "cross_section_m2": area,
            "velocity_m_s": velocity,
            "reynolds": reynolds,
            "friction_factor": friction_factor,
            "pressure_drop_pa": pressure_drop,
            "water_density_kg_m3": self.water_density,
            "dynamic_viscosity_pa_s": self.water_viscosity,
        }, "Water branch evaluated with the canonical Reynolds/Darcy-Weisbach model.")

    def calculate_heating(self, zone: HeatingZone) -> EngineeringResult:
        delta_t = zone.design_supply_temp_c - zone.design_return_temp_c
        mean_water_temp = (zone.design_supply_temp_c + zone.design_return_temp_c) / 2.0
        if delta_t <= 0.0:
            return EngineeringResult("heating", zone.id, "INPUT_REQUIRED", {"design_delta_t_k": delta_t}, "Supply temperature must exceed return temperature.")

        requested_load = zone.room_heat_load_w
        requested_mass_flow = zone.mass_flow_kg_s
        if requested_load is None and requested_mass_flow is None:
            return EngineeringResult("heating", zone.id, "INPUT_REQUIRED", {
                "design_delta_t_k": delta_t,
                "mean_water_temperature_c": mean_water_temp,
                "required_input": "mass_flow_kg_s or room_heat_load_w",
            }, "Heating heat rate requires mass flow or a room heat load.")

        calculated_mass_flow = None if requested_load is None else requested_load / (self.WATER_CP_J_KG_K * delta_t)
        calculated_heat_load = None if requested_mass_flow is None else requested_mass_flow * self.WATER_CP_J_KG_K * delta_t

        if requested_load is not None and requested_mass_flow is not None:
            assert calculated_heat_load is not None
            tolerance = max(abs(requested_load), 1.0) * self.HEATING_INPUT_REL_TOL
            if abs(calculated_heat_load - requested_load) > tolerance:
                return EngineeringResult("heating", zone.id, "INPUT_CONFLICT", {
                    "design_delta_t_k": delta_t,
                    "mean_water_temperature_c": mean_water_temp,
                    "room_heat_load_w": requested_load,
                    "heat_rate_w": calculated_heat_load,
                    "heat_rate_kw": calculated_heat_load / 1000.0,
                    "mass_flow_kg_s": requested_mass_flow,
                    "implied_heat_load_w": calculated_heat_load,
                    "heat_load_difference_w": calculated_heat_load - requested_load,
                }, "Provided room heat load and mass flow are inconsistent; they are not mutually consistent within 1%.")

        heat_load = requested_load if requested_load is not None else calculated_heat_load
        mass_flow = requested_mass_flow if requested_mass_flow is not None else calculated_mass_flow
        assert heat_load is not None and mass_flow is not None
        return EngineeringResult("heating", zone.id, "CALCULATED", {
            "design_delta_t_k": delta_t,
            "mean_water_temperature_c": mean_water_temp,
            "cp_j_kg_k": self.WATER_CP_J_KG_K,
            "room_heat_load_w": heat_load,
            "heat_rate_w": heat_load,
            "heat_rate_kw": heat_load / 1000.0,
            "mass_flow_kg_s": mass_flow,
            "emitter_type": zone.emitter_type,
        }, "Heating zone heat rate and mass flow evaluated from the declared design inputs.")

    def calculate(self, object_type: str, obj: object) -> EngineeringResult:
        if object_type == "ventilation" and isinstance(obj, VentilationOpening):
            return self.calculate_ventilation(obj)
        if object_type == "water" and isinstance(obj, WaterBranch):
            return self.calculate_water(obj)
        if object_type == "heating" and isinstance(obj, HeatingZone):
            return self.calculate_heating(obj)
        raise TypeError(f"Unsupported MEP object for calculation: {object_type}")


__all__ = ["EngineeringResult", "EngineeringResultRegistry", "MEPEngineeringService", "ensure_engineering_results"]
