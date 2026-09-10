"""Adversarial proof of the GUI 3-D -> canonical scene boundary."""

from types import SimpleNamespace

import lat_ces.gui as gui_module
from lat_ces.gui import LATCESApp
from lat_ces.visualization_3d_adapter import to_building_scene_3d


class _FakeCanvas:
    def delete(self, *_args) -> None:
        pass

    def winfo_width(self) -> int:
        return 800

    def winfo_height(self) -> int:
        return 600

    def create_line(self, *_args, **_kwargs) -> None:
        pass

    def create_polygon(self, *_args, **_kwargs) -> None:
        pass

    def create_text(self, *_args, **_kwargs) -> None:
        pass


def test_gui_3d_must_render_from_canonical_scene_not_parallel_geometry(monkeypatch) -> None:
    """Fail if draw_3d bypasses the canonical BuildingModel -> 3-D scene boundary."""

    workflow = LATCESApp.new_workflow()
    workflow.set_roof(
        "Četverovodni",
        2.50,
        construction="Drvena konstrukcija",
        covering="Crijep",
        length_m=10.0,
        width_m=10.0,
        slope_deg=25.0,
    )
    model = workflow.model

    calls = []

    def spy(model_arg):
        calls.append(model_arg.model_id)
        return to_building_scene_3d(model_arg)

    # The production GUI must expose/use this canonical boundary.
    monkeypatch.setattr(gui_module, "to_building_scene_3d", spy, raising=False)

    # Adversarially remove the parallel geometry path. If draw_3d still depends
    # on build_geometry(), this test must fail: that is the boundary we want to see.
    def forbidden_parallel_geometry(_model):
        raise AssertionError("GUI 3D bypassed canonical BuildingScene3D")

    monkeypatch.setattr(gui_module, "build_geometry", forbidden_parallel_geometry)

    app = LATCESApp.__new__(LATCESApp)
    app.workflow = workflow
    app.canvas = _FakeCanvas()
    app.view_style_var = SimpleNamespace(get=lambda: "natural")
    app.project_3d = lambda x, y, z, scale, width, height: (x, y)
    app.draw_compass = lambda: None

    app.draw_3d()

    assert calls == [model.model_id]
