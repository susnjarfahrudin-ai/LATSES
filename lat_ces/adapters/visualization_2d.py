"""2D projection of the canonical renderer-neutral visualization scene."""
from __future__ import annotations

from typing import Any, Dict, Iterable

SCHEMA = "latces.visualization.2d.v1"


def adapt_scene_2d(scene: Dict[str, Any]) -> Dict[str, Any]:
    """Project ``scene.v1`` to renderer-neutral 2D wall/room primitives.

    The input remains authoritative only as a source of representation data;
    this adapter does not calculate or mutate engineering values.
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
                    "x1_m": placement["x1_m"],
                    "y1_m": placement["y1_m"],
                    "x2_m": placement["x2_m"],
                    "y2_m": placement["y2_m"],
                    "thickness_m": wall["thickness_m"],
                    "openings": list(wall.get("openings", [])),
                }
            )
        levels.append(
            {
                "id": level["id"],
                "name": level["name"],
                "width_m": level["width_m"],
                "length_m": level["length_m"],
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
