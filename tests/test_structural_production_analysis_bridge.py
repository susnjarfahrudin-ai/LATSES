from lat_ces.building.model import BuildingModel, Level
from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.structural.production_analysis_bridge import to_production_structural_input


def test_production_model_is_preserved_and_projected_to_structural_input():
    model = BuildingModel(name="Production bridge test")
    level = Level(name="Ground floor", elevation=0.0, height=3.0)
    floor_plan = FloorPlan(name="Ground floor plan")
    wall = Wall(
        name="Load-bearing wall",
        segment=Segment2D(Point2D(0.0, 0.0), Point2D(6.0, 0.0)),
        thickness=0.25,
        load_bearing=True,
        exterior=True,
        room_ids=("room-1",),
    )
    floor_plan.add_wall(wall)
    level.set_floor_plan(floor_plan)
    model.add_level(level)

    analysis_input = to_production_structural_input(model)

    assert analysis_input.model is model
    assert len(analysis_input.building.walls) == 1
    projected_wall = analysis_input.building.walls[0]
    assert projected_wall.wall_id == wall.wall_id
    assert projected_wall.thickness_m == 0.25
    assert projected_wall.load_bearing is True
    assert projected_wall.product_id == "UNSPECIFIED"


def test_projection_does_not_mutate_production_model():
    model = BuildingModel(name="Production bridge test")
    before = dict(model.__dict__)

    analysis_input = to_production_structural_input(model)

    assert analysis_input.model is model
    assert model.__dict__ == before
