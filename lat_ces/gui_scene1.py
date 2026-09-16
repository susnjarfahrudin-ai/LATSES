"""Scene 1 integration entry point for the canonical LAT-CES workspace."""

from __future__ import annotations

from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.scene1_gui_mixin import Scene1GUIMixin


class Scene1CompleteBuildingWorkspaceApp(Scene1GUIMixin, CompleteBuildingWorkspaceApp):
    """Canonical workspace exposed through the reusable Scene 1 GUI boundary."""

    def __init__(self) -> None:
        super().__init__()
        self._init_scene1_gui()


def main() -> None:
    app = Scene1CompleteBuildingWorkspaceApp()
    app.mainloop()


__all__ = ["Scene1CompleteBuildingWorkspaceApp", "main"]
