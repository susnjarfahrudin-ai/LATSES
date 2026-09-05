"""Aggregate engineering report built from BuildingModel-owned results."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_engineering import EngineeringResult, MEPEngineeringService, ensure_engineering_results
from lat_ces.building.thermal_envelope import calculate_envelope_thermal_results, validate_thermal_result


@dataclass(frozen=True)
class BuildingEngineeringReport:
    result_count: int
    calculated_count: int
    input_required_count: int
    conflict_count: int
    validation_failure_count: int
    total_ventilation_flow_m3_h: float
    total_heating_load_w: float
    total_water_pressure_drop_pa: float
    total_opaque_wall_heat_loss_w: float
    results: tuple[EngineeringResult, ...]

    @property
    def status(self) -> str:
        if self.conflict_count:
            return "INPUT_CONFLICT"
        if self.validation_failure_count:
            return "VALIDATION_FAILED"
        if self.input_required_count:
            return "INPUT_REQUIRED"
        return "CALCULATED"


def build_building_engineering_report(
    model: object,
    *,
    service: MEPEngineeringService | None = None,
    indoor_temperature_c: float = 20.0,
    outdoor_temperature_c: float = -10.0,
) -> BuildingEngineeringReport:
    """Evaluate canonical MEP and opaque-envelope engineering results."""
    registry = ensure_mep_registry(model)
    service = service or MEPEngineeringService()
    results: list[EngineeringResult] = []

    for opening in registry.all_ventilation_openings:
        result = service.calculate_ventilation(opening)
        results.append(
            EngineeringResult(
                **{**result.__dict__, "building_model_id": getattr(model, "model_id", None)}
            )
        )
    for branch in registry.all_water_branches:
        result = service.calculate_water(branch)
        results.append(
            EngineeringResult(
                **{**result.__dict__, "building_model_id": getattr(model, "model_id", None)}
            )
        )
    for zone in registry.all_heating_zones:
        result = service.calculate_heating(zone)
        results.append(
            EngineeringResult(
                **{**result.__dict__, "building_model_id": getattr(model, "model_id", None)}
            )
        )

    thermal_results = calculate_envelope_thermal_results(
        model,
        indoor_temperature_c=indoor_temperature_c,
        outdoor_temperature_c=outdoor_temperature_c,
    )
    results.extend(thermal_results)

    result_registry = ensure_engineering_results(registry)
    for result in results:
        result_registry.put(result)

    validation_failures: list[str] = []
    for result in thermal_results:
        validation_failures.extend(validate_thermal_result(result))

    calculated_count = sum(result.status == "CALCULATED" for result in results)
    input_required_count = sum(result.status == "INPUT_REQUIRED" for result in results)
    conflict_count = sum(result.status == "INPUT_CONFLICT" for result in results)
    total_ventilation_flow_m3_h = sum(
        float(result.values.get("design_flow_m3_h", 0.0))
        for result in results
        if result.object_type == "ventilation"
    )
    total_heating_load_w = sum(
        float(result.values.get("heat_rate_w", 0.0) or 0.0)
        for result in results
        if result.object_type == "heating" and result.status == "CALCULATED"
    )
    total_water_pressure_drop_pa = sum(
        float(result.values.get("pressure_drop_pa", 0.0) or 0.0)
        for result in results
        if result.object_type == "water" and result.status == "CALCULATED"
    )
    total_opaque_wall_heat_loss_w = sum(
        float(result.values.get("heat_loss_w", 0.0) or 0.0)
        for result in results
        if result.object_type == "thermal_wall" and result.status == "CALCULATED"
    )

    report = BuildingEngineeringReport(
        result_count=len(results),
        calculated_count=calculated_count,
        input_required_count=input_required_count,
        conflict_count=conflict_count,
        validation_failure_count=len(validation_failures),
        total_ventilation_flow_m3_h=total_ventilation_flow_m3_h,
        total_heating_load_w=total_heating_load_w,
        total_water_pressure_drop_pa=total_water_pressure_drop_pa,
        total_opaque_wall_heat_loss_w=total_opaque_wall_heat_loss_w,
        results=tuple(results),
    )
    setattr(model, "building_engineering_report", report)
    return report


__all__ = ["BuildingEngineeringReport", "build_building_engineering_report"]
