"""Transparent room heat-loss projection from the canonical BuildingModel.

This first layer calculates conductive envelope wall losses only. It deliberately
requires explicit indoor/outdoor design temperatures and reports missing
window/floor/roof data instead of inventing them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lat_ces.building_model.source_of_truth import build_read_only_views


@dataclass(frozen=True)
class ThermalDesignConditions:
    indoor_temperature_c: float
    outdoor_temperature_c: float

    @property
    def delta_t_k(self) -> float:
        return self.indoor_temperature_c - self.outdoor_temperature_c

    def __post_init__(self) -> None:
        if self.indoor_temperature_c <= self.outdoor_temperature_c:
            raise ValueError("indoor design temperature must exceed outdoor design temperature")


@dataclass(frozen=True)
class RoomHeatLoss:
    room_id: str
    room_name: str
    wall_area_m2: float
    calculated_wall_loss_w: float
    heat_loss_w_m2: float
    status: str
    findings: tuple[str, ...]


@dataclass(frozen=True)
class BuildingThermalResult:
    rooms: tuple[RoomHeatLoss, ...]
    status: str
    calculated_room_count: int
    input_required_room_count: int


R_SI_M2K_W = 0.13
R_SE_M2K_W = 0.04


def _wall_u_value(thickness_m: float, lambda_w_mk: float | None) -> float:
    if lambda_w_mk is None or lambda_w_mk <= 0:
        raise ValueError("thermal conductivity is missing or invalid")
    if thickness_m <= 0:
        raise ValueError("wall thickness must be positive")
    return 1.0 / (R_SI_M2K_W + thickness_m / lambda_w_mk + R_SE_M2K_W)


def calculate_room_heat_losses(
    model: Any,
    conditions: ThermalDesignConditions,
) -> BuildingThermalResult:
    """Calculate conductive exterior-wall losses for every canonical room."""
    views = build_read_only_views(model)
    material_map = {material.product_id: material for material in views.material_views}
    losses: dict[str, float] = {room.room_id: 0.0 for room in views.room_views}
    areas: dict[str, float] = {room.room_id: 0.0 for room in views.room_views}
    findings: dict[str, list[str]] = {room.room_id: [] for room in views.room_views}

    for wall in views.wall_views:
        if not wall.exterior:
            continue
        material = material_map.get(wall.product_id)
        if material is None or material.thermal_conductivity_w_mk is None:
            for room_id in wall.room_ids:
                if room_id in findings:
                    findings[room_id].append(
                        f"{wall.wall_id}: nedostaje verificirana λ vrijednost za {wall.product_id}"
                    )
            continue
        u_value = _wall_u_value(wall.thickness_m, material.thermal_conductivity_w_mk)
        area = wall.length_m * wall.height_m
        room_ids = [room_id for room_id in wall.room_ids if room_id in losses]
        if not room_ids:
            continue
        per_room_area = area / len(room_ids)
        per_room_loss = u_value * per_room_area * conditions.delta_t_k
        for room_id in room_ids:
            areas[room_id] += per_room_area
            losses[room_id] += per_room_loss

    results: list[RoomHeatLoss] = []
    for room in views.room_views:
        findings_for_room = list(findings[room.room_id])
        status = "INPUT_REQUIRED" if findings_for_room else "CALCULATED"
        wall_loss = losses[room.room_id]
        results.append(
            RoomHeatLoss(
                room_id=room.room_id,
                room_name=room.name,
                wall_area_m2=areas[room.room_id],
                calculated_wall_loss_w=wall_loss,
                heat_loss_w_m2=(wall_loss / room.floor_area_m2 if room.floor_area_m2 > 0 else 0.0),
                status=status,
                findings=tuple(findings_for_room),
            )
        )

    calculated = sum(result.status == "CALCULATED" for result in results)
    required = sum(result.status == "INPUT_REQUIRED" for result in results)
    return BuildingThermalResult(
        rooms=tuple(results),
        status="INPUT_REQUIRED" if required else "CALCULATED",
        calculated_room_count=calculated,
        input_required_room_count=required,
    )


__all__ = [
    "BuildingThermalResult",
    "RoomHeatLoss",
    "R_SE_M2K_W",
    "R_SI_M2K_W",
    "ThermalDesignConditions",
    "calculate_room_heat_losses",
]
