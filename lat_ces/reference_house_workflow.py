"""Canonical Reference House -> current BuildingWorkflow loader.

The fixture provides authoritative building-envelope and level dimensions.
Room areas are intentionally not turned into guessed room rectangles.
"""
from __future__ import annotations

from lat_ces.building.model import BuildingModel, Level, Roof
from lat_ces.building.workflow import BuildingWorkflow, make_envelope_floor_plan
from lat_ces.reference_house import ReferenceHouse


def build_reference_house_workflow() -> BuildingWorkflow:
    house = ReferenceHouse.default()
    dimensions = house.data["dimensions"]
    length_m = float(dimensions["length_m"])
    width_m = float(dimensions["width_m"])
    height_m = float(dimensions["level_height_m"])

    model = BuildingModel(name=house.data["name"])

    for index, level_data in enumerate(house.levels):
        loads = level_data.get("loads", {})
        level = Level(
            name=level_data["name"],
            elevation=index * height_m,
            height=height_m,
            length_m=length_m,
            width_m=width_m,
            dead_load_kpa=float(loads.get("dead_kpa", 0.0)),
            live_load_kpa=float(loads.get("live_kpa", 0.0)),
        )
        level.set_floor_plan(make_envelope_floor_plan(level.name, length_m, width_m, 0.25))
        model.add_level(level)

    roof_data = house.data.get("roof", {})
    model.set_roof(
        Roof(
            roof_type=str(roof_data.get("type", "dvovodni")),
            covering=str(roof_data.get("covering", "")),
            length_m=length_m,
            width_m=width_m,
            slope_deg=float(roof_data.get("slope_deg", 0.0)),
            height_m=0.0,
        )
    )

    return BuildingWorkflow(
        model=model,
        current_step=3,
        active_level_id=next(iter(model.levels), None),
    )


__all__ = ["build_reference_house_workflow"]
