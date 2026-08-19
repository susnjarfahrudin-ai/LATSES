from pathlib import Path

import pytest

from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry3d import build_level_geometry
from lat_ces.building.model import BuildingModel, Level
from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.workflow import BuildingWorkflow


def test_opening_has_explicit_height() -> None:
    opening = Opening(kind="window", offset=1.0, width=1.2, height_m=1.4)
    assert opening.width == 1.2
    assert opening.height_m == 1.4


def test_opening_height_round_trips_through_workflow_json(tmp_path: Path) -> None:
    plan = FloorPlan("Prizemlje")
    wall = Wall("Vanjski zid", Segment2D(Point2D(0, 0), Point2D(10, 0)))
    wall.add_opening(Opening(kind="door", offset=2.0, width=0.9, height_m=2.1))
    plan.add_wall(wall)

    model = BuildingModel("Test objekat")
    level = Level("Prizemlje", elevation=0.0, height=2.8, length_m=10.0, width_m=10.0, floor_plan=plan)
    model.add_level(level)
    workflow = BuildingWorkflow(model=model, active_level_id=level.level_id)

    path = tmp_path / "building.json"
    save_workflow(workflow, path)
    loaded = load_workflow(path)
    loaded_opening = next(iter(loaded.floor_plan.walls.values())).openings[0]

    assert loaded_opening.kind == "door"
    assert loaded_opening.width == 0.9
    assert loaded_opening.height_m == 2.1


def test_3d_geometry_keeps_opening_as_void_metadata() -> None:
    plan = FloorPlan("Prizemlje")
    wall = Wall("Vanjski zid", Segment2D(Point2D(0, 0), Point2D(10, 0)), thickness=0.20)
    wall.add_opening(Opening(kind="door", offset=2.0, width=1.0, height_m=2.1))
    plan.add_wall(wall)
    level = Level("Prizemlje", elevation=0.0, height=2.8, length_m=10.0, width_m=10.0, floor_plan=plan)

    geometry = build_level_geometry(level)
    extruded = geometry.walls[0]

    assert len(extruded.openings) == 1
    assert extruded.openings[0].height_m == 2.1
    assert extruded.gross_area == pytest.approx(28.0)
    assert extruded.net_area == pytest.approx(25.9)
    assert extruded.net_volume == pytest.approx(5.18)


def test_3d_geometry_rejects_opening_taller_than_level() -> None:
    plan = FloorPlan("Prizemlje")
    wall = Wall("Vanjski zid", Segment2D(Point2D(0, 0), Point2D(5, 0)))
    wall.add_opening(Opening(kind="door", offset=1.0, width=0.9, height_m=2.9))
    plan.add_wall(wall)
    level = Level("Prizemlje", elevation=0.0, height=2.8, length_m=5.0, width_m=5.0, floor_plan=plan)

    with pytest.raises(ValueError, match="opening height"):
        build_level_geometry(level)
