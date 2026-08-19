"""Preliminary structural load take-off for the BuildingModel.

This is a traceable load-input layer, not a final code-compliance or member-sizing
solver. It computes self-weight plus explicitly supplied tributary floor/roof loads
for load-bearing walls so a future structural analysis engine has clean inputs.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StructuralWallLoad:
    wall_id: str
    wall_name: str
    level_id: str
    self_weight_kn_m: float
    tributary_floor_load_kn_m: float
    tributary_roof_load_kn_m: float
    total_line_load_kn_m: float


@dataclass(frozen=True)
class StructuralLoadReport:
    status: str
    walls: tuple[StructuralWallLoad, ...]
    total_vertical_line_load_kn_m: float
    findings: tuple[str, ...] = ()


def _wall_self_weight_kn_m(wall, level_height: float, density_kg_m3: float) -> float:
    opening_area_per_length = sum(item.width * item.height_m for item in wall.openings) / max(wall.segment.length, 1e-9)
    clear_height = max(0.0, level_height - opening_area_per_length)
    volume_per_length = wall.thickness * clear_height
    return density_kg_m3 * volume_per_length * 9.80665 / 1000.0


def calculate_structural_loads(model) -> StructuralLoadReport:
    """Return preliminary vertical line loads for explicitly marked load-bearing walls."""
    loads: list[StructuralWallLoad] = []
    findings: list[str] = []
    levels = list(model.levels.values())

    for level_index, level in enumerate(levels):
        plan = level.floor_plan
        if plan is None:
            continue
        for wall in plan.walls.values():
            if not wall.load_bearing:
                continue
            if wall.tributary_width_m <= 0.0:
                findings.append(f"{wall.name}: unesena tributarna širina")
                continue
            if not wall.material_id or wall.material_id not in model.materials:
                findings.append(f"{wall.name}: nije odabran materijal")
                continue
            material = model.materials[wall.material_id]
            if material.density is None:
                findings.append(f"{wall.name}: materijal nema gustinu")
                continue

            self_weight = _wall_self_weight_kn_m(wall, level.height, material.density)
            floor_load = max(0.0, level.dead_load_kpa + level.live_load_kpa) * wall.tributary_width_m
            roof_load = 0.0
            if level_index == len(levels) - 1 and model.roof is not None:
                roof = model.roof
                roof_load = max(0.0, roof.dead_load_kpa + roof.snow_load_kpa) * wall.tributary_width_m

            total = self_weight + floor_load + roof_load
            loads.append(
                StructuralWallLoad(
                    wall_id=wall.wall_id,
                    wall_name=wall.name,
                    level_id=level.level_id,
                    self_weight_kn_m=round(self_weight, 3),
                    tributary_floor_load_kn_m=round(floor_load, 3),
                    tributary_roof_load_kn_m=round(roof_load, 3),
                    total_line_load_kn_m=round(total, 3),
                )
            )

    status = "CALCULATED" if loads and not findings else "INPUT_REQUIRED"
    report = StructuralLoadReport(
        status=status,
        walls=tuple(loads),
        total_vertical_line_load_kn_m=round(sum(item.total_line_load_kn_m for item in loads), 3),
        findings=tuple(findings),
    )
    model.structural_load_report = report
    return report


__all__ = ["StructuralWallLoad", "StructuralLoadReport", "calculate_structural_loads"]
