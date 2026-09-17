"""Adversarial tests for the reconstructed GUI communication boundary."""

from __future__ import annotations

import ast
from pathlib import Path

from lat_ces.gui_architecture.adapters import (
    PreparedGUICommandAdapter,
    Scene1Adapter,
    ThreeDHandoffAdapter,
)
from lat_ces.gui_architecture.contracts import (
    BoundaryStatus,
    GUICommand,
    GUIEvent,
    GUIResult,
    GUIState,
)


ROOT = Path(__file__).resolve().parents[1]
GUI_MIXIN = ROOT / "lat_ces" / "scene1_gui_mixin.py"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def test_gui_contracts_are_transport_only():
    command = GUICommand(command="export_3d", payload={"format": "blender"})
    event = GUIEvent(event="export_completed")
    result = GUIResult(status="READY", events=(event,))
    state = GUIState(view="model", selected_id="WALL-1")

    assert command.source == "GUI"
    assert result.events == (event,)
    assert state.selected_id == "WALL-1"
    assert result.status == "READY"


def test_gui_mixin_has_no_direct_presentation_or_external_tool_imports():
    imports = _imports(GUI_MIXIN)
    assert "lat_ces.adapters.building_visualization" not in imports
    assert "lat_ces.presentation_controller" not in imports
    assert "lat_ces.visualization_3d_external" not in imports
    assert "lat_ces.gui_architecture.adapters" in imports


def test_prepared_command_boundary_is_explicitly_not_connected():
    adapter = PreparedGUICommandAdapter()
    assert adapter.status is BoundaryStatus.NOT_YET_CONNECTED
    try:
        adapter.dispatch(GUICommand(command="future_command"))
    except NotImplementedError as exc:
        assert "NOT_YET_CONNECTED" in str(exc)
    else:
        raise AssertionError("Prepared GUI command boundary must not invent a consumer")


def test_existing_boundaries_are_explicitly_connected():
    assert Scene1Adapter.status is BoundaryStatus.CONNECTED
    assert ThreeDHandoffAdapter.status is BoundaryStatus.CONNECTED


def test_gui_architecture_contracts_do_not_define_a_building_model():
    contracts = (ROOT / "lat_ces" / "gui_architecture" / "contracts.py").read_text(encoding="utf-8")
    assert "class BuildingModel" not in contracts
    assert "from lat_ces.building.model import BuildingModel" not in contracts
