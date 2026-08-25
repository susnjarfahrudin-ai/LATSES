"""Canonical Reference House -> BuildingModel factory.

The Reference House fixture is a deterministic project input. This module is
its only conversion boundary into the canonical BuildingModel so GUI layers do
not invent a second geometry model.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .geometry import Box3D, Point3D
from .model import BuildingModel, Level, Room, Roof
from .orientation import BuildingOrientation
from .workflow import make_envelope_floor_plan


def _load_fixture() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[1] / "reference_house_model.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _partition_rows(rooms: list[dict[str, Any]], row_count: int = 3) -> list[list[dict[str, Any]]]:
    rows: list[list[dict[str, Any]]] = [[] for _ in range(min(row_count, max(1, len(rooms))))]
    row_areas = [0.0] * len(rows)
    for room in rooms:
        index = min(range(len(rows)), key=lambda i: row_areas[i])
        rows[index].append(room)
        row_areas[index] += float(room["area_m2"])
    return [row for row in rows if row]


def _add_rooms(level: Level, room_data: list[dict[str, Any]]) -> None:
    """Tile conditioned rooms across the usable floor envelope while preserving area."""
    wall = 0.20
    inner_length = max(level.length_m - 2 * wall, 0.1)
    conditioned = [room for room in room_data if float(room.get("height_m", 0.0)) > 0.0]
    rows = _partition_rows(conditioned)
    y = wall
    for row in rows:
        row_area = sum(float(room["area_m2"]) for room in row)
        row_height = row_area / inner_length
        x = wall
        for room in row:
            area = float(room["area_m2"])
            room_width = area / row_height
            level.add_room(
                Room(
                    name=str(room["name"]),
                    footprint=Box3D(
                        Point3D(x, y, 0.0),
                        room_width,
                        row_height,
                        float(room["height_m"]),
                    ),
                )
            )
            x += room_width
        y += row_height


def load_reference_house_model() -> tuple[BuildingModel, dict[str, Any]]:
    """Build the canonical BuildingModel from the deterministic fixture."""
    data = _load_fixture()
    dimensions = data["dimensions"]
    model = BuildingModel(name=data["name"])
    model.set_orientation(BuildingOrientation(north_azimuth_deg=0.0))

    for level_data in data["levels"]:
        level = Level(
            name=level_data["name"],
            elevation=0.0,
            height=float(dimensions["level_height_m"]),
            length_m=float(dimensions["length_m"]),
            width_m=float(dimensions["width_m"]),
            facade_finish=data["envelope"]["exterior_wall"]["facade_finish"],
            insulation_material=data["envelope"]["exterior_wall"]["insulation"],
            insulation_thickness_m=float(data["envelope"]["exterior_wall"]["insulation_thickness_m"]),
            interior_plaster_material=data["envelope"]["exterior_wall"]["interior_finish"],
            interior_plaster_thickness_m=float(data["envelope"]["exterior_wall"]["interior_finish_thickness_m"]),
            dead_load_kpa=float(level_data["loads"]["dead_kpa"]),
            live_load_kpa=float(level_data["loads"]["live_kpa"]),
            floor_plan=make_envelope_floor_plan(
                level_data["name"],
                float(dimensions["length_m"]),
                float(dimensions["width_m"]),
                0.20,
            ),
        )
        previous = list(model.levels.values())[-1] if model.levels else None
        level.elevation = previous.top_elevation if previous else 0.0
        _add_rooms(level, level_data["rooms"])
        model.add_level(level)

    roof = data["roof"]
    width = float(dimensions["width_m"])
    slope = float(roof["slope_deg"])
    model.set_roof(
        Roof(
            roof_type=str(roof["type"]),
            construction="drvena konstrukcija",
            covering=str(roof["covering"]),
            substructure="letve + kontra-letve",
            support="krovna ploča / vijenci",
            length_m=float(dimensions["length_m"]),
            width_m=width,
            slope_deg=slope,
            height_m=(width / 2.0) * math.tan(math.radians(slope)),
        )
    )
    return model, data


__all__ = ["load_reference_house_model"]
