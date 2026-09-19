"""Native Scene 1 presentation boundary.

Consumes renderer-neutral ``scene.v1`` data and produces only 2D
presentation primitives.  It has no write path to BuildingModel.
"""

from __future__ import annotations

from typing import Any, Mapping


class Scene1NativePresentation:
    """One-way adapter from ``scene.v1`` to native 2D presentation data."""

    def present(self, scene: Mapping[str, Any]) -> dict[str, Any]:
        if scene.get("schema") != "scene.v1":
            raise ValueError("Scene 1 requires scene.v1")

        projection = scene.get("projection", {})
        return {
            "scene": "scene1",
            "primitives": {
                "walls": list(projection.get("walls", [])),
                "openings": list(projection.get("openings", [])),
                "rooms": list(projection.get("rooms", [])),
            },
        }


__all__ = ["Scene1NativePresentation"]
