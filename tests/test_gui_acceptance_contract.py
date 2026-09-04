from __future__ import annotations

from lat_ces.building.floor_plan import FloorPlan
from lat_ces.building.model import BuildingModel
from lat_ces.gui import FloorPlanEditor, LATCESApp
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp, main


def test_production_gui_entrypoint_is_complete_workspace() -> None:
    """The installed GUI command must resolve directly to the canonical workspace."""
    assert CompleteBuildingWorkspaceApp.__mro__[1] is not object
    assert issubclass(CompleteBuildingWorkspaceApp, LATCESApp)
    assert callable(main)


def test_gui_model_path_is_single_canonical_building_model() -> None:
    """Reference GUI workflow starts from one BuildingModel and one FloorPlan."""
    workflow = LATCESApp.new_workflow()
    model = workflow.model

    assert isinstance(model, BuildingModel)
    assert model.name == "Novi objekat"
    assert len(model.levels) == 1
    level = workflow.active_level
    assert level.floor_plan is not None
    assert isinstance(level.floor_plan, FloorPlan)
    assert workflow.floor_plan is level.floor_plan
    assert level.floor_plan.wall_count == 4
    assert all(wall.exterior for wall in level.floor_plan.walls.values())


def test_floor_plan_editor_targets_the_same_workflow_floor_plan() -> None:
    workflow = LATCESApp.new_workflow()

    class AppProbe:
        def __init__(self) -> None:
            self.workflow = workflow

    editor = FloorPlanEditor(AppProbe())
    assert editor.floor_plan is workflow.floor_plan


def test_no_obsolete_reference_house_json_is_required_by_canonical_gui() -> None:
    """The canonical GUI path must not depend on the retired fixture JSON packaging path."""
    import inspect
    import lat_ces.gui_complete as gui_complete

    source = inspect.getsource(gui_complete)
    assert "reference_house_model.json" not in source
    assert "gui_release" not in source
    assert "gui_functional" not in source
    assert "gui_master" not in source
