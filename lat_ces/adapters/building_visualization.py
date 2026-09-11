"""Renderer-neutral projection of authoritative BuildingModel geometry."""
from typing import Any, Dict

from lat_ces.building.model import BuildingModel


class BuildingVisualizationAdapter:
    """Expose only geometry that is authoritative in BuildingModel."""

    def adapt(self, model: BuildingModel) -> Dict[str, Any]:
        levels = []
        for level in model.levels.values():
            walls = []
            floor_plan = level.floor_plan
            if floor_plan is not None:
                for wall in floor_plan.walls.values():
                    start = wall.segment.start
                    end = wall.segment.end
                    item: Dict[str, Any] = {
                        "id": wall.wall_id,
                        "length_m": wall.segment.length,
                        "thickness_m": wall.thickness,
                        "height_m": level.height,
                        "exterior": wall.exterior,
                        "load_bearing": wall.load_bearing,
                        "openings": [
                            {
                                "kind": opening.kind,
                                "width_m": opening.width,
                                "height_m": opening.height_m,
                                "position_m": opening.offset,
                            }
                            for opening in wall.openings
                        ],
                        "placement": {
                            "x1_m": start.x,
                            "y1_m": start.y,
                            "x2_m": end.x,
                            "y2_m": end.y,
                        },
                    }
                    walls.append(item)

            levels.append(
                {
                    "id": level.level_id,
                    "name": level.name,
                    "length_m": level.length_m,
                    "width_m": level.width_m,
                    "height_m": level.height,
                    "rooms": [
                        {
                            "id": room.room_id,
                            "name": room.name,
                            "length_m": room.footprint.length,
                            "width_m": room.footprint.width,
                            "height_m": room.footprint.height,
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
