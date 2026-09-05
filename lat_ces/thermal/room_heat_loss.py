"""Transparent room heat-loss projection from the canonical BuildingModel.

This first layer calculates conductive envelope wall losses only. It deliberately
requires explicit indoor/outdoor design temperatures and reports missing
window/floor/roof data instead of inventing them.
"""Room-level opaque exterior-wall heat-loss projection.

The calculation consumes the canonical BuildingModel geometry and material
records. It deliberately covers opaque wall conduction only; windows, doors,
roof, floor and ventilation are separate heat-loss terms and are not silently
invented here.
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
from math import isfinite
from typing import Any

from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.catalog.product_catalog import get_product


DEFAULT_R_SI_M2K_W = 0.13
DEFAULT_R_SE_M2K_W = 0.04
_TOL = 1e-9


@dataclass(frozen=True)
class RoomHeatLossResult:
    room_id: str
    room_name: str
    level_name: str
    floor_area_m2: float
    exterior_wall_area_m2: float
    u_value_w_m2k: float | None
    design_delta_t_k: float | None
    heat_loss_w: float | None
    heat_loss_w_m2: float | None
    status: str
    findings: tuple[str, ...] = ()


def _material_for_wall(model: Any, wall: Any):
    return model.materials.get(wall.material_id) if wall.material_id else None


def _conductivity_for_wall(model: Any, wall: Any) -> float | None:
    material = _material_for_wall(model, wall)
    if material is not None and material.thermal_conductivity is not None:
        return material.thermal_conductivity

    registry = ensure_product_binding_registry(model)
    binding = registry.get(wall.wall_id)
    if binding is not None:
        product = get_product(binding.product_id)
        if product is not None and product.thermal_conductivity_w_mk is not None:
            return product.thermal_conductivity_w_mk
    return None


def _wall_room_overlap_m(wall: Any, room: Any) -> float:
    """Return the physical overlap length between an exterior wall and room footprint."""
    x0 = room.footprint.origin.x
    x1 = x0 + room.footprint.length
    y0 = room.footprint.origin.y
    y1 = y0 + room.footprint.width

    wx0 = wall.segment.start.x
    wy0 = wall.segment.start.y
    wx1 = wall.segment.end.x
    wy1 = wall.segment.end.y

    if abs(wy0 - wy1) <= _TOL:
        if not (abs(wy0 - y0) <= _TOL or abs(wy0 - y1) <= _TOL):
            return 0.0
        wall_min, wall_max = sorted((wx0, wx1))
        return max(0.0, min(wall_max, x1) - max(wall_min, x0))

    if abs(wx0 - wx1) <= _TOL:
        if not (abs(wx0 - x0) <= _TOL or abs(wx0 - x1) <= _TOL):
            return 0.0
        wall_min, wall_max = sorted((wy0, wy1))
        return max(0.0, min(wall_max, y1) - max(wall_min, y0))

    raise ValueError("Only axis-aligned walls are supported by the current room heat-loss adapter")


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
    *,
    design_indoor_c: float,
    design_outdoor_c: float,
    r_si_m2k_w: float = DEFAULT_R_SI_M2K_W,
    r_se_m2k_w: float = DEFAULT_R_SE_M2K_W,
) -> tuple[RoomHeatLossResult, ...]:
    """Calculate opaque exterior-wall transmission heat loss per room.

    ``Q_wall = U * A_wall * DeltaT`` and ``W/m²`` is reported against the
    room's canonical floor area. Missing lambda or invalid design temperatures
    remain explicit ``INPUT_REQUIRED`` instead of being replaced with guesses.
    """
    if not isfinite(design_indoor_c) or not isfinite(design_outdoor_c):
        raise ValueError("Design temperatures must be finite")
    if design_indoor_c <= design_outdoor_c:
        raise ValueError("Design indoor temperature must be above outdoor temperature")
    if r_si_m2k_w <= 0 or r_se_m2k_w < 0:
        raise ValueError("Surface resistances must be positive/non-negative")

    delta_t = design_indoor_c - design_outdoor_c
    results: list[RoomHeatLossResult] = []

    for level in model.levels.values():
        if level.floor_plan is None:
            continue
        exterior_walls = [wall for wall in level.floor_plan.walls.values() if wall.exterior]
        for room in level.rooms.values():
            area_m2 = 0.0
            conductivities: list[float] = []
            findings: list[str] = []

            for wall in exterior_walls:
                overlap_m = _wall_room_overlap_m(wall, room)
                if overlap_m <= _TOL:
                    continue
                area_m2 += overlap_m * level.height
                conductivity = _conductivity_for_wall(model, wall)
                if conductivity is None:
                    findings.append(f"nedostaje λ za zid {wall.name}")
                else:
                    conductivities.append(conductivity)

            if area_m2 <= _TOL:
                results.append(
                    RoomHeatLossResult(
                        room_id=room.room_id,
                        room_name=room.name,
                        level_name=level.name,
                        floor_area_m2=room.floor_area,
                        exterior_wall_area_m2=0.0,
                        u_value_w_m2k=None,
                        design_delta_t_k=delta_t,
                        heat_loss_w=0.0,
                        heat_loss_w_m2=0.0,
                        status="NO_EXTERIOR_WALL_AREA",
                        findings=("prostorija nema geometrijski dokazanu vanjsku zidnu površinu",),
                    )
                )
                continue

            if findings or not conductivities:
                results.append(
                    RoomHeatLossResult(
                        room_id=room.room_id,
                        room_name=room.name,
                        level_name=level.name,
                        floor_area_m2=room.floor_area,
                        exterior_wall_area_m2=area_m2,
                        u_value_w_m2k=None,
                        design_delta_t_k=delta_t,
                        heat_loss_w=None,
                        heat_loss_w_m2=None,
                        status="INPUT_REQUIRED",
                        findings=tuple(dict.fromkeys(findings)),
                    )
                )
                continue

            # All currently supported room exterior walls use one canonical
            # opaque assembly. Mixed lambda assemblies are held at the input
            # gate until an explicit area-weighted assembly model is present.
            if any(abs(value - conductivities[0]) > _TOL for value in conductivities[1:]):
                results.append(
                    RoomHeatLossResult(
                        room_id=room.room_id,
                        room_name=room.name,
                        level_name=level.name,
                        floor_area_m2=room.floor_area,
                        exterior_wall_area_m2=area_m2,
                        u_value_w_m2k=None,
                        design_delta_t_k=delta_t,
                        heat_loss_w=None,
                        heat_loss_w_m2=None,
                        status="INPUT_REQUIRED",
                        findings=("prostorija koristi više λ vrijednosti na vanjskom zidu; potreban area-weighted assembly obračun",),
                    )
                )
                continue

            conductivity = conductivities[0]
            thickness = wall_thickness_for_room(model, level, room)
            resistance = r_si_m2k_w + thickness / conductivity + r_se_m2k_w
            u_value = 1.0 / resistance
            heat_loss_w = u_value * area_m2 * delta_t
            results.append(
                RoomHeatLossResult(
                    room_id=room.room_id,
                    room_name=room.name,
                    level_name=level.name,
                    floor_area_m2=room.floor_area,
                    exterior_wall_area_m2=area_m2,
                    u_value_w_m2k=u_value,
                    design_delta_t_k=delta_t,
                    heat_loss_w=heat_loss_w,
                    heat_loss_w_m2=heat_loss_w / room.floor_area if room.floor_area > 0 else None,
                    status="CALCULATED",
                    findings=(),
                )
            )

    return tuple(results)


def wall_thickness_for_room(model: Any, level: Any, room: Any) -> float:
    """Resolve one canonical exterior-wall thickness for a room."""
    if level.floor_plan is None:
        raise ValueError("Level has no floor plan")
    thicknesses: list[float] = []
    for wall in level.floor_plan.walls.values():
        if wall.exterior and _wall_room_overlap_m(wall, room) > _TOL:
            thicknesses.append(wall.thickness)
    if not thicknesses:
        raise ValueError(f"Room {room.room_id} has no exterior wall")
    first = thicknesses[0]
    if any(abs(value - first) > _TOL for value in thicknesses[1:]):
        raise ValueError("Room uses multiple exterior wall thicknesses; assembly weighting is required")
    return first


__all__ = [
    "DEFAULT_R_SI_M2K_W",
    "DEFAULT_R_SE_M2K_W",
    "RoomHeatLossResult",
    "calculate_room_heat_losses",
]
