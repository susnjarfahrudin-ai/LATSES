from lat_ces.adapters.building_visualization import BuildingVisualizationAdapter
from lat_ces.building_model import BuildingModel
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.presentation_controller import PresentationController


class Scene1CompleteBuildingWorkspaceApp(CompleteBuildingWorkspaceApp):
    """Production Scene 1 wrapper using the canonical BuildingModel flow."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._presentation_controller = PresentationController()

    def show_scene1(self) -> None:
        """Render the current canonical scene snapshot on the existing canvas."""
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
            (item for item in levels if item["id"] == self.active_level.id),
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
        offset_x = (width - span_x * scale) / 2.0
        offset_y = (height - span_y * scale) / 2.0

        for wall in walls:
            x1 = offset_x + (wall["x1_m"] - min_x) * scale
            y1 = height - (offset_y + (wall["y1_m"] - min_y) * scale)
            x2 = offset_x + (wall["x2_m"] - min_x) * scale
            y2 = height - (offset_y + (wall["y2_m"] - min_y) * scale)
            self.canvas.create_line(x1, y1, x2, y2, tags="scene1")

        self.canvas.create_text(
            width / 2,
            margin / 2,
            text=level.get("name", level["id"]),
            tags="scene1",
        )
        self.status_var.set("Scene 1: BuildingModel → scene.v1 → controller → 2D")


def main() -> None:
    app = Scene1CompleteBuildingWorkspaceApp()
    app.mainloop()
