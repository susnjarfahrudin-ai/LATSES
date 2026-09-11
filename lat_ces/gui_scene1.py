"""Scene 1 integration for the existing Complete LAT-CES workspace.

This module reuses the existing Tkinter workspace; it does not create a
second GUI architecture. Scene 1 receives a fresh renderer-neutral snapshot
from BuildingModel and draws only presentation primitives onto the existing
canvas.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.adapters.building_visualization import BuildingVisualizationAdapter
from lat_ces.adapters.visualization_2d import adapt_scene_2d
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp


class Scene1CompleteBuildingWorkspaceApp(CompleteBuildingWorkspaceApp):
    """Existing LAT-CES workspace with the real Scene 1 canvas hook."""

    def __init__(self) -> None:
        super().__init__()
        self._install_scene1_control()

    def _install_scene1_control(self) -> None:
        """Add one Scene 1 action to the existing Model / Pogledi tab."""
        if not hasattr(self, "complete_tabs"):
            return
        tab_id = self.complete_tabs.tabs()[0]
        tab = self.nametowidget(tab_id)
        ttk.Button(tab, text="Scene 1 — stvarni model", command=self.show_scene1).pack(
            side="left", padx=(12, 2)
        )

    def show_scene1(self) -> None:
        """Render the current BuildingModel snapshot on the existing canvas."""
        scene = BuildingVisualizationAdapter().adapt(self.workflow.model)
        scene_2d = adapt_scene_2d(scene)

        self.canvas.delete("scene1")
        width = max(self.canvas.winfo_width(), 400)
        height = max(self.canvas.winfo_height(), 300)
        margin = 35.0

        levels = scene_2d.get("levels", [])
        if not levels:
            self.status_var.set("Scene 1: nema etaža za prikaz")
            return

        level = next(
            (item for item in levels if item["id"] == self.active_level.level_id),
            levels[0],
        )
        walls = level.get("walls", [])
        if not walls:
            self.status_var.set("Scene 1: nema geometrije zida za prikaz")
            return

        xs = [p for wall in walls for p in (wall["x1_m"], wall["x2_m"])]
        ys = [p for wall in walls for p in (wall["y1_m"], wall["y2_m"])]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(max_x - min_x, 0.001)
        span_y = max(max_y - min_y, 0.001)
        scale = min((width - 2 * margin) / span_x, (height - 2 * margin) / span_y)

        def point(x_m: float, y_m: float) -> tuple[float, float]:
            return (
                margin + (x_m - min_x) * scale,
                height - margin - (y_m - min_y) * scale,
            )

        for wall in walls:
            x1, y1 = point(wall["x1_m"], wall["y1_m"])
            x2, y2 = point(wall["x2_m"], wall["y2_m"])
            self.canvas.create_line(
                x1, y1, x2, y2, width=max(1, wall["thickness_m"] * scale), tags="scene1"
            )

        self.canvas.create_text(
            margin,
            margin / 2,
            anchor="w",
            text=f"Scene 1 · {level['name']} · BuildingModel snapshot",
            tags="scene1",
        )
        self.status_var.set("Scene 1: prikazan direktno iz BuildingModel → scene.v1 → 2D")


def main() -> None:
    app = Scene1CompleteBuildingWorkspaceApp()
    app.mainloop()


__all__ = ["Scene1CompleteBuildingWorkspaceApp", "main"]
