"""Reusable Scene 1 GUI integration for the canonical workspace."""

from __future__ import annotations

from tkinter import filedialog, ttk

from lat_ces.gui_architecture.adapters import Scene1Adapter, ThreeDHandoffAdapter


class Scene1GUIMixin:
    """Expose GUI actions while keeping Scene 1 communication behind adapters."""

    def _init_scene1_gui(self) -> None:
        if not hasattr(self, "_scene1_adapter"):
            self._scene1_adapter = Scene1Adapter()
        if not hasattr(self, "_three_d_handoff_adapter"):
            self._three_d_handoff_adapter = ThreeDHandoffAdapter()
        self._install_scene1_control()

    def _install_scene1_control(self) -> None:
        """Add user-facing actions without exposing core/presentation APIs."""
        if not hasattr(self, "complete_tabs"):
            return
        tab_id = self.complete_tabs.tabs()[0]
        tab = self.nametowidget(tab_id)
        children = tab.winfo_children()
        manager = children[0].winfo_manager() if children else "pack"
        toolbar = ttk.Frame(tab)
        if manager == "grid":
            toolbar.grid(row=0, column=99, sticky="w", padx=8, pady=2)
        else:
            toolbar.pack(side="left", padx=(12, 2))

        ttk.Button(toolbar, text="Novi materijal", command=self._open_material_input).pack(side="left", padx=2)
        ttk.Button(toolbar, text="3D vizualizacija objekta", command=lambda: self._set_view_step(5)).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Scene 1 — stvarni model", command=self.show_scene1).pack(side="left", padx=2)
        ttk.Button(toolbar, text="3D → Blender JSON", command=self.export_scene3d_to_blender).pack(side="left", padx=2)

    def show_scene1(self) -> None:
        """Request the approved Scene 1 presentation of the canonical model."""
        scene_2d = self._scene1_adapter.present_model(self.workflow.model)

        self.canvas.delete("scene1")
        width = max(self.canvas.winfo_width(), 400)
        height = max(self.canvas.winfo_height(), 300)
        margin = 35.0

        levels = scene_2d.get("levels", [])
        if not levels:
            self.status_var.set("Scene 1: nema etaža za prikaz")
            return

        level = next((item for item in levels if item["id"] == self.active_level.level_id), levels[0])
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
            return (margin + (x_m - min_x) * scale, height - margin - (y_m - min_y) * scale)

        for wall in walls:
            x1, y1 = point(wall["x1_m"], wall["y1_m"])
            x2, y2 = point(wall["x2_m"], wall["y2_m"])
            self.canvas.create_line(x1, y1, x2, y2, width=max(1, wall["thickness_m"] * scale), tags="scene1")

        self.canvas.create_text(
            margin, margin / 2, anchor="w",
            text=f"Scene 1 · {level['name']} · BuildingModel snapshot", tags="scene1"
        )
        self.status_var.set("Scene 1: BuildingModel → Scene1Adapter → 2D presentation")

    def export_scene3d_to_blender(self) -> None:
        """Request the approved external handoff without knowing its implementation."""
        target = filedialog.asksaveasfilename(
            parent=self,
            title="Izvezi LAT-CES 3D za Blender",
            defaultextension=".json",
            filetypes=(("LAT-CES Blender scene", "*.json"), ("JSON", "*.json"), ("All files", "*.*")),
            initialfile="latces_scene3d_blender.json",
        )
        if not target:
            return
        result = self._three_d_handoff_adapter.export(self.workflow.model, target)
        self.status_var.set(f"3D handoff: {result.status} · {target}")
