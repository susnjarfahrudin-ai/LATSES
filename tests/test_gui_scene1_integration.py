from dataclasses import dataclass
from pathlib import Path

from lat_ces.adapters.building_visualization import BuildingVisualizationAdapter
from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level
from lat_ces.building.workflow import BuildingWorkflow
from lat_ces.gui_scene1 import Scene1CompleteBuildingWorkspaceApp
from lat_ces.presentation_controller import PresentationController


def test_scene1_gui_reuses_existing_workspace_and_controller():
    assert Scene1CompleteBuildingWorkspaceApp.__mro__[1].__name__ == "CompleteBuildingWorkspaceApp"
    assert "_presentation_controller" in Scene1CompleteBuildingWorkspaceApp.__init__.__code__.co_names
    assert "present_scene_1" in Scene1CompleteBuildingWorkspaceApp.show_scene1.__code__.co_names


def test_default_gui_entry_points_to_scene1_wrapper():
    text = Path("pyproject.toml").read_text(encoding="utf-8")
    assert 'lat-ces-gui = "lat_ces.gui_scene1:main"' in text


@dataclass
class _FakeCanvas:
    deleted: list[str]
    lines: list[tuple]
    texts: list[tuple]

    def delete(self, tag: str) -> None:
        self.deleted.append(tag)

    def winfo_width(self) -> int:
        return 800

    def winfo_height(self) -> int:
        return 600

    def create_line(self, *args, **kwargs):
        self.lines.append((args, kwargs))

    def create_text(self, *args, **kwargs):
        self.texts.append((args, kwargs))


def _make_model() -> BuildingModel:
    floor_plan = FloorPlan("Prizemlje")
    for name, start, end in (
        ("W1", Point2D(0.0, 0.0), Point2D(10.0, 0.0)),
        ("W2", Point2D(10.0, 0.0), Point2D(10.0, 8.0)),
        ("W3", Point2D(10.0, 8.0), Point2D(0.0, 8.0)),
        ("W4", Point2D(0.0, 8.0), Point2D(0.0, 0.0)),
    ):
        floor_plan.add_wall(
            Wall(
                name,
                Segment2D(start, end),
                thickness=0.20,
                exterior=True,
                load_bearing=True,
            )
        )

    level = Level(
        "Prizemlje",
        0.0,
        2.8,
        length_m=10.0,
        width_m=8.0,
        floor_plan=floor_plan,
    )
    model = BuildingModel(name="Testni objekat")
    model.add_level(level)
    return model


def test_scene1_show_uses_canonical_snapshot_and_does_not_write_model():
    model = _make_model()
    level = next(iter(model.levels.values()))
    before = (
        model.name,
        tuple(model.levels),
        level.length_m,
        level.width_m,
        tuple(level.floor_plan.walls),
    )

    scene = BuildingVisualizationAdapter().adapt(model)
    assert scene["schema"] == "latces.visualization.scene.v1"

    app = Scene1CompleteBuildingWorkspaceApp.__new__(Scene1CompleteBuildingWorkspaceApp)
    workflow = BuildingWorkflow(model=model)
    workflow.set_active_level(level.level_id)
    app.workflow = workflow
    app._presentation_controller = PresentationController()
    app.canvas = _FakeCanvas([], [], [])
    app.status_var = type("Status", (), {"value": "", "set": lambda self, value: setattr(self, "value", value)})()

    app.show_scene1()

    assert app.canvas.lines
    assert app.canvas.texts
    assert app.canvas.deleted == ["scene1"]
    assert app.status_var.value == "Scene 1: BuildingModel → scene.v1 → controller → 2D"
    assert (
        model.name,
        tuple(model.levels),
        level.length_m,
        level.width_m,
        tuple(level.floor_plan.walls),
    ) == before


def test_scene1_information_direction_is_canonical_scene_to_2d_only():
    model = _make_model()
    scene = BuildingVisualizationAdapter().adapt(model)
    payload = PresentationController().present_scene_1(scene)

    assert scene["schema"] == "latces.visualization.scene.v1"
    assert payload["schema"] == "latces.visualization.2d.v1"
    assert payload["source_schema"] == scene["schema"]
    assert payload["source"] == scene["source"]
