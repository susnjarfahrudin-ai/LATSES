"""Unified Building Engineering Report over one canonical BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.electrical import ElectricalReport, calculate_electrical_report
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_engineering import EngineeringResult, MEPEngineeringService, ensure_engineering_results
from lat_ces.building.quantity_takeoff import BuildingQuantityTakeoff, calculate_quantity_takeoff
from lat_ces.building.structural import StructuralLoadReport, calculate_structural_loads
from lat_ces.building.thermal import EnvelopeThermalReport, calculate_envelope_thermal


@dataclass(frozen=True)
class BuildingEngineeringReport:
    result_count: int
    calculated_count: int
    input_required_count: int
    conflict_count: int
    total_ventilation_flow_m3_h: float
    total_heating_load_w: float
    total_water_pressure_drop_pa: float
    results: tuple[EngineeringResult, ...]
    quantities: BuildingQuantityTakeoff
    structural: StructuralLoadReport
    thermal: EnvelopeThermalReport
    electrical: ElectricalReport

    @property
    def status(self) -> str:
        """Return the status of the requested MEP engineering aggregation.

        Structural, thermal, electrical and quantity-takeoff domains are
        reported alongside MEP, but missing inputs in those optional domains
        must not invalidate otherwise calculated MEP results.  Their own
        status remains available on the corresponding report object.
        """
        if self.conflict_count:
            return "INPUT_CONFLICT"
        if self.input_required_count:
            return "INPUT_REQUIRED"
        return "CALCULATED"


def build_building_engineering_report(
    model: object,
    *,
    service: MEPEngineeringService | None = None,
    design_delta_t_k: float = 30.0,
) -> BuildingEngineeringReport:
    """Evaluate all available domains against the same BuildingModel."""
    registry = ensure_mep_registry(model)
    service = service or MEPEngineeringService()
    results: list[EngineeringResult] = []

    for opening in registry.all_ventilation_openings:
        results.append(service.calculate_ventilation(opening))
    for branch in registry.all_water_branches:
        results.append(service.calculate_water(branch))
    for zone in registry.all_heating_zones:
        results.append(service.calculate_heating(zone))

    result_registry = ensure_engineering_results(registry)
    for result in results:
        result_registry.put(result)

    calculated_count = sum(result.status == "CALCULATED" for result in results)
    input_required_count = sum(result.status == "INPUT_REQUIRED" for result in results)
    conflict_count = sum(result.status == "INPUT_CONFLICT" for result in results)

    quantities = calculate_quantity_takeoff(model)
    structural = calculate_structural_loads(model)
    thermal = calculate_envelope_thermal(model, design_delta_t_k=design_delta_t_k)
    electrical = calculate_electrical_report(model)

    report = BuildingEngineeringReport(
        result_count=len(results),
        calculated_count=calculated_count,
        input_required_count=input_required_count,
        conflict_count=conflict_count,
        total_ventilation_flow_m3_h=sum(
            float(result.values.get("design_flow_m3_h", 0.0))
            for result in results
            if result.object_type == "ventilation"
        ),
        total_heating_load_w=sum(
            float(result.values.get("heat_rate_w", 0.0) or 0.0)
            for result in results
            if result.object_type == "heating" and result.status == "CALCULATED"
        ),
        total_water_pressure_drop_pa=sum(
            float(result.values.get("pressure_drop_pa", 0.0) or 0.0)
            for result in results
            if result.object_type == "water" and result.status == "CALCULATED"
        ),
        results=tuple(results),
        quantities=quantities,
        structural=structural,
        thermal=thermal,
        electrical=electrical,
    )
    setattr(model, "building_engineering_report", report)
    return report


__all__ = ["BuildingEngineeringReport", "build_building_engineering_report"]
