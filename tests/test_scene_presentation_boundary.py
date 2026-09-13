"""Verification of the one-way Scene 1/Scene 2 presentation boundary."""

import json
from pathlib import Path

from lat_ces.adapters import (
    Scene1PresentationBoundary,
    Scene2PresentationBoundary,
    adapt_building,
)
from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level


def _scene() -> dict:
    model = BuildingModel(name="Boundary House")
    level = Level(
        name="Ground",
        elevation=0.0,
        height=3.0,
        level_id="ground",
        length_m=10.0,
        width_m=8.0,
        floor_plan=FloorPlan(name="Ground Plan"),
    )
    level.floor_plan.add_wall(
        Wall(
            name="South",
            wall_id="south",
            segment=Segment2D(Point2D(0.0, 0.0), Point2D(10.0, 0.0)),
            thickness=0.30,
            exterior=True,
        )
    )
    model.add_level(level)
    return adapt_building(model)


def test_scene1_is_downstream_only() -> None:
    scene = _scene()
    original = json.loads(json.dumps(scene))

    payload = Scene1PresentationBoundary().present(scene)

    assert payload["source_schema"] == scene["schema"]
    assert payload["source"] == scene["source"]
    assert scene == original
    assert payload is not scene


def test_scene2_exports_only_derived_payload(tmp_path: Path) -> None:
    scene = _scene()
    original = json.loads(json.dumps(scene))
    output = tmp_path / "scene2.json"

    result = Scene2PresentationBoundary().export(scene, output)

    assert result == output
    exported = json.loads(output.read_text(encoding="utf-8"))
    assert exported["source_schema"] == scene["schema"]
    assert exported["source"] == scene["source"]
    assert exported["schema"] == "latces.visualization.3d.v1"
    assert scene == original


def test_external_renderer_receives_file_path_only(tmp_path: Path) -> None:
    scene = _scene()
    output = tmp_path / "scene2.json"
    boundary = Scene2PresentationBoundary()

    process = boundary.launch(scene, output, ["python", "-c", "import sys; print(sys.argv[1])"])
    stdout, _ = process.communicate(timeout=10)

    assert stdout.decode().strip() == str(output)
