"""Compatibility adapter from the existing BuildingModel to BuildingConcept.

The adapter is intentionally one-way.  It lets existing engineering models
consume the new canonical concept without introducing a second geometry
implementation.
"""
from __future__ import annotations

from .concept import BuildingConcept, LevelKind, MaterialSelection, OpeningSpec
from .core import BuildingModel


def to_concept(model: BuildingModel) -> BuildingConcept:
    concept = BuildingConcept(model.name)

    for level_id, level in model.levels.items():
        kind = _level_kind(level.name)
        concept.add_level(level_id, kind, level.length_m, level.width_m, level.height_m)
        for room_id, room in level.rooms.items():
            concept.add_room(room_id, level_id, room.length_m, room.width_m)
        for wall in level.walls.values():
            for index, opening in enumerate(wall.openings):
                opening_id = f"{wall.id}:opening:{index}"
                concept.openings[opening_id] = OpeningSpec(
                    id=opening_id,
                    kind=opening.kind,
                    width_m=opening.width_m,
                    height_m=opening.height_m,
                    sill_height_m=opening.sill_height_m,
                )

    for material_id, material in model.materials.items():
        concept.materials[material_id] = MaterialSelection(
            category="building-material",
            material=material.name,
            density_kg_m3=material.density_kg_m3,
        )
    return concept


def _level_kind(name: str) -> LevelKind:
    value = name.strip().lower()
    if "podrum" in value or "basement" in value or "suter" in value:
        return LevelKind.BASEMENT
    if "prizem" in value or "ground" in value:
        return LevelKind.GROUND
    if "krov" in value or "roof" in value:
        return LevelKind.ROOF
    if "temelj" in value or "foundation" in value:
        return LevelKind.FOUNDATION
    return LevelKind.FLOOR
