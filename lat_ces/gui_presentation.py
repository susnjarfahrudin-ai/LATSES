"""Explicit GUI presentation extensions over canonical scene snapshots.

Presentation extensions own rendering/export orchestration only. They do not
own BuildingModel state and never return presentation data to engineering
state.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from lat_ces.adapters.building_visualization import BuildingVisualizationAdapter
from lat_ces.presentation_controller import PresentationController
from lat_ces.visualization_3d_external import write_blender_exchange


class Scene1PresentationExtension:
    """Render the canonical Scene 1 projection on an existing Tk canvas."""

    def __init__(self, controller: PresentationController | None = None) -> None:
        self.controller = controller or PresentationController()

    def render(self, model: Any, canvas: Any, active_level_id: str | None = None) -> bool:
        scene = BuildingVisualizationAdapter().adapt(model)
        scene_2d = self.controller.present_scene_1(scene)
        canvas.delete("scene1")
        width = max(canvas.winfo_width(), 400)
        height = max(canvas.winfo_height(), 300)
        margin = 35.0
        levels = scene_2d.get("levels", [])
        if not levels:
            return False
        level = next((item for item in levels if item["id"] == active_level_id), levels[0])
        walls = level.get("walls", [])
        if not walls:
            return False
        xs = [p for wall in walls for p in (wall["x1_m"], wall["x2_m"])]
        ys = [p for wall in walls for p in (wall["y1_m"], wall["y2_m"])]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 0.001)
        span_y = max(max_y - min_y, 0.001)
        scale = min((width - 2 * margin) / span_x, (height - 2 * margin) / span_y)

        def point(x_m: float, y_m: float) -> tuple[float, float]:
            return (margin + (x_m - min_x) * scale, height - margin - (y_m - min_y) * scale)

        for wall in walls:
            x1, y1 = point(wall["x1_m"], wall["y1_m"])
            x2, y2 = point(wall["x2_m"], wall["y2_m"])
            canvas.create_line(x1, y1, x2, y2, width=max(1, wall["thickness_m"] * scale), tags="scene1")
        canvas.create_text(
            margin,
            margin / 2,
            anchor="w",
            text=f"Scene 1 · {level['name']} · BuildingModel snapshot",
            tags="scene1",
        )
        return True


class Scene2PresentationExtension:
    """Export a canonical scene projection to an external 3-D consumer."""

    def __init__(self, controller: PresentationController | None = None) -> None:
        self.controller = controller or PresentationController()

    def export(self, model: Any, path: Path) -> Path:
        scene = BuildingVisualizationAdapter().adapt(model)
        return self.controller.export_scene_2(scene, path)

    def export_blender_exchange(self, model: Any, path: str) -> None:
        """Compatibility handoff for the existing Blender exchange contract."""
        write_blender_exchange(model, path)
