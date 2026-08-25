"""Contextual presentation data for the canonical LAT-CES GUI.

This module deliberately contains presentation mapping only. It does not own
BuildingModel state, perform engineering calculations, or create a second
model. GUI widgets can consume these compact dictionaries while scientific and
engineering calculations remain in their canonical domain modules.
"""
from __future__ import annotations

from typing import Any


def _round_value(value: float, digits: int = 3) -> float:
    return round(float(value), digits)


def selected_wall_properties(model: Any, wall: Any | None) -> dict[str, Any]:
    """Return display-ready properties for one canonical wall."""
    if wall is None:
        return {"selection": "Nije odabran objekat"}

    material_name = "—"
    material_id = getattr(wall, "material_id", None)
    materials = getattr(model, "materials", {})
    material = materials.get(material_id) if material_id else None
    if material is not None:
        material_name = getattr(material, "name", "—")

    segment = getattr(wall, "segment", None)
    length = getattr(segment, "length", 0.0) if segment is not None else 0.0
    return {
        "selection": "Wall",
        "name": getattr(wall, "name", "Wall"),
        "length_m": _round_value(length),
        "thickness_m": _round_value(getattr(wall, "thickness", 0.0)),
        "height_m": _round_value(getattr(wall, "height", 0.0)),
        "load_bearing": bool(getattr(wall, "load_bearing", False)),
        "tributary_width_m": _round_value(getattr(wall, "tributary_width_m", 0.0)),
        "material": material_name,
        "opening_count": len(getattr(wall, "openings", ()) or ()),
    }


def model_context(model: Any) -> dict[str, Any]:
    """Return a compact BuildingModel summary for a persistent status panel."""
    levels = tuple(getattr(model, "levels", {}).values())
    current_level = levels[0] if levels else None
    return {
        "building": getattr(model, "name", "LAT-CES"),
        "level_count": len(levels),
        "active_level": getattr(current_level, "name", "—"),
        "floor_count": sum(1 for level in levels if getattr(level, "floor_plan", None) is not None),
        "wall_count": sum(getattr(level.floor_plan, "wall_count", 0) for level in levels if getattr(level, "floor_plan", None) is not None),
        "room_count": sum(len(getattr(level, "rooms", {})) for level in levels),
        "material_count": len(getattr(model, "materials", {})),
    }


def engineering_context(report: Any | None) -> dict[str, Any]:
    """Return display-ready aggregate engineering values from an existing report."""
    if report is None:
        return {
            "status": "NO_RESULT",
            "ventilation_m3_h": 0.0,
            "heating_w": 0.0,
            "water_pressure_drop_pa": 0.0,
            "calculated_count": 0,
            "input_required_count": 0,
            "conflict_count": 0,
        }
    return {
        "status": getattr(report, "status", "UNKNOWN"),
        "ventilation_m3_h": _round_value(getattr(report, "total_ventilation_flow_m3_h", 0.0)),
        "heating_w": _round_value(getattr(report, "total_heating_load_w", 0.0)),
        "water_pressure_drop_pa": _round_value(getattr(report, "total_water_pressure_drop_pa", 0.0)),
        "calculated_count": int(getattr(report, "calculated_count", 0)),
        "input_required_count": int(getattr(report, "input_required_count", 0)),
        "conflict_count": int(getattr(report, "conflict_count", 0)),
    }


__all__ = ["selected_wall_properties", "model_context", "engineering_context"]
