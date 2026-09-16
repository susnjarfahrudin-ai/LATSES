"""Reusable Scene 1 GUI integration for the canonical workspace."""

from __future__ import annotations

from tkinter import filedialog, ttk

from lat_ces.adapters.building_visualization import BuildingVisualizationAdapter
from lat_ces.presentation_controller import PresentationController
from lat_ces.visualization_3d_external import write_blender_exchange


class Scene1GUIMixin:
    """Adds the canonical Scene 1 presentation boundary to a workspace."""

    def _init_scene1_gui(self) -> None:
        self._presentation_controller = PresentationController()
        self._install_scene1_control()

    def _install_scene1_control(self) -> None:
        """Add the existing model actions plus the canonical Scene 1 actions."""
        if not hasattr(self, "complete_tabs"):
            return
        tab_id = self.complete_tabs.tabs()[0]
        tab = self.nametowidget(tab_id)
        ttk.Button(
            tab,
            text="Novi materijal",
            command=self._open_material_input,
        ).pack(side="left", padx=(12, 2))
        ttk.Button(
            tab,
            text="3D vizualizacija objekta",
            command=lambda: self._set_view_step(5),
        ).pack(side="left", padx=2)
        ttk.Button(
            tab,
            text="Scene 1 — stvarni model",
            command=self.show_scene1,
        ).pack(side="left", padx=2)
        ttk.Button(
            tab,
            text="3D → Blender JSON",
            command=self.export_scene3d_to_blender,
        ).pack(side="left", padx=2)

    def show_scene1(self) -> None:
        """Render the current canonical BuildingModel snapshot through Scene 1."""
        scene = BuildingVisualizationAdapter().adapt(self.workflow.model)
        scene_2d = self._presentation_controller.present_scene_1(scene)

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
                x1,
                y1,
                x2,
                y2,
                width=max(1, wall["thickness_m"] * scale),
                tags="scene1",
            )

        self.canvas.create_text(
            margin,
            margin / 2,
            anchor="w",
            text=f"Scene 1 · {level['name']} · BuildingModel snapshot",
            tags="scene1",
        )
        self.status_var.set("Scene 1: BuildingModel → scene.v1 → controller → 2D")

    def export_scene3d_to_blender(self) -> None:
        """Export the canonical 3-D scene through the existing Blender boundary."""
        target = filedialog.asksaveasfilename(
            parent=self,
            title="Izvezi LAT-CES 3D za Blender",
            defaultextension=".json",
            filetypes=(("LAT-CES Blender scene", "*.json"), ("JSON", "*.json"), ("All files", "*.*")),
            initialfile="latces_scene3d_blender.json",
        )
        if not target:
            return
        write_blender_exchange(self.workflow.model, target)
        self.status_var.set(f"3D handoff izvezen: {target}")
