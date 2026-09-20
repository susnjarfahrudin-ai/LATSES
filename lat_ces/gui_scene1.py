"""Scene 1 integration for the existing Complete LAT-CES workspace.

The production GUI remains one workspace. Presentation behavior is delegated
to explicit presentation extensions; engineering state remains owned by the
canonical BuildingModel/workflow.
"""
from __future__ import annotations

from tkinter import filedialog, ttk

from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.gui_product_catalog import ProductCatalogMixin
from lat_ces.gui_presentation import Scene1PresentationExtension, Scene2PresentationExtension
from lat_ces.presentation_controller import PresentationController


class Scene1CompleteBuildingWorkspaceApp(CompleteBuildingWorkspaceApp, ProductCatalogMixin):
    """Existing LAT-CES workspace with explicit presentation extensions."""

    def __init__(self) -> None:
        super().__init__()
        controller = PresentationController()
        self._scene1_presentation = Scene1PresentationExtension(controller)
        self._scene2_presentation = Scene2PresentationExtension(controller)
        self._install_scene1_control()
        self._install_product_catalog_tab()

    def _install_scene1_control(self) -> None:
        """Add primary 3-D and Scene 1 actions to the model tab."""
        if not hasattr(self, "complete_tabs"):
            return
        tab_id = self.complete_tabs.tabs()[0]
        tab = self.nametowidget(tab_id)
        ttk.Button(tab, text="3D vizualizacija objekta", command=lambda: self._set_view_step(5)).pack(side="left", padx=2)
        ttk.Button(tab, text="Scene 1 — stvarni model", command=self.show_scene1).pack(side="left", padx=2)
        ttk.Button(tab, text="3D → Blender JSON", command=self.export_scene3d_to_blender).pack(side="left", padx=2)

    def show_scene1(self) -> None:
        """Render only through the explicit Scene 1 presentation extension."""
        rendered = self._scene1_presentation.render(
            self.workflow.model,
            self.canvas,
            self.active_level.level_id,
        )
        if not rendered:
            self.status_var.set("Scene 1: nema geometrije za prikaz")
            return
        self.status_var.set("Scene 1: BuildingModel → presentation extension → 2D")

    def export_scene3d_to_blender(self) -> None:
        """Export the current canonical 3-D scene through the presentation extension."""
        target = filedialog.asksaveasfilename(
            parent=self,
            title="Izvezi LAT-CES 3D za Blender",
            defaultextension=".json",
            filetypes=(("LAT-CES Blender scene", "*.json"), ("JSON", "*.json"), ("All files", "*.*")),
            initialfile="latces_scene3d_blender.json",
        )
        if not target:
            return
        self._scene2_presentation.export_blender_exchange(self.workflow.model, target)
        self.status_var.set(f"3D handoff izvezen: {target}")


def main() -> None:
    app = Scene1CompleteBuildingWorkspaceApp()
    app.mainloop()


__all__ = ["Scene1CompleteBuildingWorkspaceApp", "main"]
