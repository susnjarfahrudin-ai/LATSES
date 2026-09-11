"""3D projection of the canonical renderer-neutral visualization scene."""
from __future__ import annotations

from typing import Any, Dict

SCHEMA = "latces.visualization.3d.v1"


def adapt_scene_3d(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Project ``scene.v1`` to renderer-neutral 3D solid descriptors.

    Coordinates and dimensions are copied from the visualization contract.
    No geometry is regenerated from engineering assumptions in this layer.
    """
    if scene.get("schema") != "latces.visualization.scene.v1":
        raise ValueError("unsupported visualization scene schema")

    levels = []
    for level in scene.get("levels", []):
        walls = []
        for wall in level.get("walls", []):
            placement = wall.get("placement")
            if placement is None:
                continue
            walls.append(
                {
                    "id": wall["id"],
                    "start_m": [placement["x1_m"], placement["y1_m"], 0.0],
                    "end_m": [placement["x2_m"], placement["y2_m"], 0.0],
                    "height_m": wall["height_m"],
                    "thickness_m": wall["thickness_m"],
                    "openings": list(wall.get("openings", [])),
                }
            )
        levels.append(
            {
                "id": level["id"],
                "name": level["name"],
                "height_m": level["height_m"],
                "rooms": list(level.get("rooms", [])),
                "walls": walls,
            }
        )

    return {
        "schema": SCHEMA,
        "source_schema": scene["schema"],
        "source": scene["source"],
        "building": dict(scene.get("building", {})),
        "levels": levels,
    }
