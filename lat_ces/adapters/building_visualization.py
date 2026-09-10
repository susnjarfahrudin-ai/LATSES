"""Neutral visualization adapter for the authoritative BuildingModel.

This module deliberately contains no GUI or renderer dependency. It converts
known BuildingModel facts into a renderer-neutral scene description without
inventing coordinates or engineering properties that are absent from the
source model.
"""
from typing import Any, Dict

from lat_ces.building_model import BuildingModel


class BuildingVisualizationAdapter:
    """Project BuildingModel data into a renderer-neutral representation."""

    def adapt(self, model: BuildingModel) -> Dict[str, Any]:
        levels = []
        for level in model.levels.values():
            levels.append(
                {
                    "id": level.id,
                    "name": level.name,
                    "length_m": level.length_m,
                    "width_m": level.width_m,
                    "height_m": level.height_m,
                    "rooms": [
                        {
                            "id": room.id,
                            "name": room.name,
                            "length_m": room.length_m,
                            "width_m": room.width_m,
                            "height_m": room.height_m,
                        }
                        for room in level.rooms.values()
                    ],
                    "walls": [
                        {
                            "id": wall.id,
                            "length_m": wall.length_m,
                            "thickness_m": wall.thickness_m,
                            "height_m": wall.height_m,
                            "exterior": wall.exterior,
                            "load_bearing": wall.load_bearing,
                            "openings": [
                                {
                                    "kind": opening.kind,
                                    "width_m": opening.width_m,
                                    "height_m": opening.height_m,
                                    "sill_height_m": opening.sill_height_m,
                                    "position_m": opening.position_m,
                                }
                                for opening in wall.openings
                            ],
                        }
                        for wall in level.walls.values()
                    ],
                }
            )

        return {
            "schema": "latces.visualization.scene.v1",
            "source": "BuildingModel",
            "building": {"name": model.name},
            "levels": levels,
        }


def adapt_building(model: BuildingModel) -> Dict[str, Any]:
    """Convenience function for the dependency-free visualization adapter."""
    return BuildingVisualizationAdapter().adapt(model)
