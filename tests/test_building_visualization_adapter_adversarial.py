from lat_ces.adapters import adapt_building
from lat_ces.building_model import BuildingModel, Level, Room, Wall


def _model(*, room_length: float = 6.0, wall_length: float = 10.0) -> BuildingModel:
    model = BuildingModel(name="Adversarial House")
    level = Level("L1", "Ground", 10.0, 8.0, 2.8)
    level.add_room(Room("R1", "Living", room_length, 5.0, 2.8))
    level.add_wall(Wall("W1", wall_length, 0.25, 2.8))
    model.add_level(level)
    return model


def test_adapter_must_reflect_changed_physical_dimension():
    baseline = adapt_building(_model(room_length=6.0))["levels"][0]["rooms"][0]
    changed = adapt_building(_model(room_length=6.5))["levels"][0]["rooms"][0]

    assert baseline["length_m"] == 6.0
    assert changed["length_m"] == 6.5
    assert baseline["length_m"] != changed["length_m"]


def test_adapter_must_not_invent_geometry_from_missing_source_facts():
    scene = adapt_building(_model())
    level = scene["levels"][0]
    wall = level["walls"][0]

    assert "x_m" not in wall
    assert "y_m" not in wall
    assert "z_m" not in wall
    assert "rotation_deg" not in wall
