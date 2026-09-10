"""Renderer-neutral projection of authoritative BuildingModel geometry."""
from typing import Any, Dict

from lat_ces.building_model import BuildingModel


class BuildingVisualizationAdapter:
    """Expose only geometry that is authoritative in BuildingModel."""

    def adapt(self, model: BuildingModel) -> Dict[str, Any]:
        levels = []
        for level in model.levels.values():
            walls = []
            for wall in level.walls.values():
                item: Dict[str, Any] = {
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
                if wall.placement is not None:
                    item["placement"] = {
                        "x1_m": wall.placement.x1_m,
                        "y1_m": wall.placement.y1_m,
                        "x2_m": wall.placement.x2_m,
                        "y2_m": wall.placement.y2_m,
                    }
                walls.append(item)

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
                    "walls": walls,
                }
            )

        return {
            "schema": "latces.visualization.scene.v1",
            "source": "BuildingModel",
            "building": {"name": model.name},
            "levels": levels,
        }


def adapt_building(model: BuildingModel) -> Dict[str, Any]:
    return BuildingVisualizationAdapter().adapt(model)
