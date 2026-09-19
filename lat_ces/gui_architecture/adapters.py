"""Thin adapters used by the GUI communication boundary.

These adapters intentionally reuse existing LAT-CES owners. They do not add
engineering logic and do not create a second BuildingModel authority.
"""

from __future__ import annotations

from typing import Any

from lat_ces.adapters.building_visualization import BuildingVisualizationAdapter
from lat_ces.presentation_controller import PresentationController
from lat_ces.visualization_3d_external import write_blender_exchange

from .contracts import BoundaryStatus, GUICommand, GUIResult


class Scene1Adapter:
    """GUI-facing adapter for the existing canonical Scene 1 path."""

    status = BoundaryStatus.CONNECTED

    def __init__(
        self,
        visualization: BuildingVisualizationAdapter | None = None,
        presentation: PresentationController | None = None,
    ) -> None:
        self._visualization = visualization or BuildingVisualizationAdapter()
        self._presentation = presentation or PresentationController()

    def present_model(self, model: Any) -> dict[str, Any]:
        """Translate canonical BuildingModel to the existing 2-D presentation payload."""
        scene = self._visualization.adapt(model)
        return self._presentation.present_scene_1(scene)


class ThreeDHandoffAdapter:
    """Approved GUI boundary for the existing neutral Blender handoff."""

    status = BoundaryStatus.CONNECTED

    def export(self, model: Any, target: str) -> GUIResult:
        write_blender_exchange(model, target)
        return GUIResult(status="EXPORTED", payload={"target": target})


class PreparedGUICommandAdapter:
    """Prepared command boundary; deliberately has no production consumer yet."""

    status = BoundaryStatus.NOT_YET_CONNECTED

    def dispatch(self, command: GUICommand) -> GUIResult:
        raise NotImplementedError(
            "GUI command boundary is PREPARED but NOT_YET_CONNECTED; "
            "no production consumer is defined yet."
        )
