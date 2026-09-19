from dataclasses import dataclass

from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.gui import LATCESApp


@dataclass
class _FakeCanvas:
    lines: list[tuple]
    texts: list[tuple]

    def delete(self, tag: str) -> None:
        assert tag == "all"

    def winfo_width(self) -> int:
        return 800

    def winfo_height(self) -> int:
        return 600

    def create_line(self, *args, **kwargs):
        self.lines.append((args, kwargs))

    def create_text(self, *args, **kwargs):
        self.texts.append((args, kwargs))

    def create_oval(self, *args, **kwargs):
        pass


@dataclass
class _FakeWorkflow:
    floor_plan: FloorPlan
    active_level: object


def _make_app(floor_plan: FloorPlan, selected_wall_id: str) -> LATCESApp:
    app = LATCESApp.__new__(LATCESApp)
    app.workflow = _FakeWorkflow(floor_plan, type("Level", (), {"name": "Prizemlje"})())
    app.editor = type("Editor", (), {"selected_wall_id": selected_wall_id})()
    app.canvas = _FakeCanvas([], [])
    app.plan_bounds = lambda: (0.0, 10.0, 0.0, 8.0)
    app.model_to_canvas = lambda point: (40.0 + point.x * 60.0, 520.0 - point.y * 60.0)
    app.draw_compass = lambda: None
    return app


def test_pr227_selected_wall_only_dimension_and_opening_labels_with_offset():
    plan = FloorPlan("Prizemlje")
    selected = plan.add_wall(
        Wall("W1", Segment2D(Point2D(0.0, 0.0), Point2D(10.0, 0.0)))
    )
    selected.add_opening(Opening(kind="door", offset=4.0, width=1.0))
    other = plan.add_wall(
        Wall("W2", Segment2D(Point2D(10.0, 0.0), Point2D(10.0, 8.0)))
    )
    other.add_opening(Opening(kind="window", offset=3.0, width=1.2))

    app = _make_app(plan, selected.wall_id)
    app.draw_floor_plan()

    text_values = [entry[1]["text"] for entry in app.canvas.texts]
    assert "10.00 m" in text_values
    assert "door 1.00 m" in text_values
    assert "8.00 m" not in text_values
    assert "window 1.20 m" not in text_values

    dimension = next(entry for entry in app.canvas.texts if entry[1]["text"] == "10.00 m")
    midpoint = ((40.0 + 640.0) / 2.0, 520.0)
    dimension_point = dimension[0][:2]
    assert dimension_point != midpoint
    assert abs(dimension_point[0] - midpoint[0]) < 1e-9
    assert abs(dimension_point[1] - (midpoint[1] + 18.0)) < 1e-9

    opening_labels = [entry for entry in app.canvas.texts if entry[1]["text"] == "door 1.00 m"]
    assert len(opening_labels) == 1
