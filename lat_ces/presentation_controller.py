"""Presentation orchestration without ownership of engineering state.

The controller receives an already-created canonical ``scene.v1`` snapshot and
routes it to the one-way Scene 1 / Scene 2 presentation boundaries.  It never
creates or mutates a ``BuildingModel`` and never accepts presentation output
back as engineering state.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .adapters.scene_presentation_boundary import (
    Scene1PresentationBoundary,
    Scene2PresentationBoundary,
)


class PresentationController:
    """Route one canonical scene snapshot to presentation consumers."""

    def __init__(
        self,
        scene1: Scene1PresentationBoundary | None = None,
        scene2: Scene2PresentationBoundary | None = None,
    ) -> None:
        self._scene1 = scene1 or Scene1PresentationBoundary()
        self._scene2 = scene2 or Scene2PresentationBoundary()

    def present_scene_1(self, scene: Mapping[str, Any]) -> Dict[str, Any]:
        """Send the canonical snapshot one-way to the Scene 1 boundary."""
        return self._scene1.present(scene)

    def export_scene_2(self, scene: Mapping[str, Any], path: Path) -> Path:
        """Send the canonical snapshot one-way to the Scene 2 export boundary."""
        return self._scene2.export(scene, path)

    def launch_scene_2(
        self,
        scene: Mapping[str, Any],
        path: Path,
        executable: Sequence[str],
    ) -> subprocess.Popen[bytes]:
        """Launch Scene 2 using only the exported presentation file."""
        return self._scene2.launch(scene, path, executable)
