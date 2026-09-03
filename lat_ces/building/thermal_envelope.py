"""Canonical envelope heat-loss calculation on the BuildingModel.

This is a transparent first vertical slice: wall material -> U -> Q. It is
intentionally limited to declared opaque exterior walls and does not invent
missing thermal inputs.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.mep_engineering import EngineeringResult

R_SI_M2_K_W = 0.13
R_SE_M2_K_W = 0.04


@dataclass(frozen=True)
class ThermalWallResult:
    wall_id: str
    level_id: str
    area_m2: float
    thickness_m: float
    thermal_conductivity_w_mk: float
    u_value_w_m2k: float
    delta_t_k: float
    heat_loss_w: float


def _net_wall_area_m2(wall, level_height: float) -> float:
    gross_area = wall.net_length * level_height
    opening_area = sum(opening.width * opening.height_m for opening in wall.openings)
    return max(0.0, gross_area - opening_area)


def _input_required(wall, values: dict, message: str) -> EngineeringResult:
    return EngineeringResult(
        object_type="thermal_wall",
        object_id=wall.wall_id,
        status="INPUT_REQUIRED",
        values=values,
        message=message,
    )


def calculate_wall_thermal_result(
    model: object,
    level: object,
    wall: object,
    *,
    indoor_temperature_c: float,
    outdoor_temperature_c: float,
) -> EngineeringResult:
    """Calculate opaque exterior-wall U-value and transmission heat loss."""
    if not getattr(wall, "exterior", False):
        return _input_required(wall, {}, "Thermal envelope calculation requires an exterior wall.")

    material_id = getattr(wall, "material_id", None)
    if not material_id or material_id not in model.materials:
        return _input_required(
            wall, {}, "Exterior wall requires a material with declared thermal conductivity."
        )

    material = model.materials[material_id]
    lam = material.thermal_conductivity
    if lam is None or lam <= 0.0:
        return _input_required(
            wall,
            {"building_model_id": model.model_id, "material_id": material_id},
            "Material thermal conductivity (lambda) is required; LAT-CES will not assume a value.",
        )

    thickness = wall.thickness
    if thickness <= 0.0:
        return _input_required(
            wall,
            {"building_model_id": model.model_id, "material_id": material_id},
            "Wall thickness must be greater than zero.",
        )

    delta_t = indoor_temperature_c - outdoor_temperature_c
    if delta_t <= 0.0:
        return _input_required(
            wall,
            {
                "building_model_id": model.model_id,
                "indoor_temperature_c": indoor_temperature_c,
                "outdoor_temperature_c": outdoor_temperature_c,
            },
            "Indoor design temperature must exceed outdoor design temperature for heat-loss evaluation.",
        )

    area = _net_wall_area_m2(wall, level.height)
    r_total = R_SI_M2_K_W + thickness / lam + R_SE_M2_K_W
    u_value = 1.0 / r_total
    heat_loss = u_value * area * delta_t

    return EngineeringResult(
        object_type="thermal_wall",
        object_id=wall.wall_id,
        status="CALCULATED",
        values={
            "building_model_id": model.model_id,
            "level_id": level.level_id,
            "material_id": material_id,
            "area_m2": area,
            "thickness_m": thickness,
            "thermal_conductivity_w_mk": lam,
            "r_si_m2k_w": R_SI_M2_K_W,
            "r_layer_m2k_w": thickness / lam,
            "r_se_m2k_w": R_SE_M2_K_W,
            "u_value_w_m2k": u_value,
            "indoor_temperature_c": indoor_temperature_c,
            "outdoor_temperature_c": outdoor_temperature_c,
            "delta_t_k": delta_t,
            "heat_loss_w": heat_loss,
            "heat_loss_kw": heat_loss / 1000.0,
        },
        message="Opaque exterior wall evaluated from declared material, thickness and design temperatures.",
        building_model_id=model.model_id,
        equation="U = 1 / (Rsi + d/lambda + Rse); Q = U * A * DeltaT",
        provenance={
            "building_model_id": model.model_id,
            "level_id": level.level_id,
            "wall_id": wall.wall_id,
            "material_id": material_id,
        },
    )


def calculate_envelope_thermal_results(
    model: object,
    *,
    indoor_temperature_c: float = 20.0,
    outdoor_temperature_c: float = -10.0,
) -> tuple[EngineeringResult, ...]:
    """Evaluate all exterior walls owned by the canonical BuildingModel."""
    results: list[EngineeringResult] = []
    for level in model.levels.values():
        if level.floor_plan is None:
            continue
        for wall in level.floor_plan.walls.values():
            if wall.exterior:
                results.append(
                    calculate_wall_thermal_result(
                        model,
                        level,
                        wall,
                        indoor_temperature_c=indoor_temperature_c,
                        outdoor_temperature_c=outdoor_temperature_c,
                    )
                )
    return tuple(results)


def validate_thermal_result(result: EngineeringResult, *, tolerance: float = 1e-9) -> tuple[str, ...]:
    """Validate the internal U*A*deltaT identity of a calculated wall result."""
    if result.status != "CALCULATED":
        return ()
    values = result.values
    expected = values["u_value_w_m2k"] * values["area_m2"] * values["delta_t_k"]
    actual = values["heat_loss_w"]
    if abs(actual - expected) > tolerance * max(1.0, abs(expected)):
        return ("THERMAL-VAL-001: heat loss does not satisfy Q = U * A * DeltaT",)
    if result.building_model_id != values.get("building_model_id"):
        return ("THERMAL-VAL-002: engineering result is detached from its BuildingModel identity",)
    if not result.equation or not result.provenance:
        return ("THERMAL-VAL-003: calculated thermal result is missing equation or provenance",)
    return ()


__all__ = [
    "R_SI_M2_K_W",
    "R_SE_M2_K_W",
    "ThermalWallResult",
    "calculate_wall_thermal_result",
    "calculate_envelope_thermal_results",
    "validate_thermal_result",
]
