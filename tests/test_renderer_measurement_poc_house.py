from lat_ces.adapters import adapt_building
from lat_ces.building_model import BuildingModel, Level, Opening, Room, Wall


def minimal_renderer_house() -> BuildingModel:
    model = BuildingModel(name="Renderer Measurement House")
    level = Level(
        id="L1",
        name="Ground floor",
        length_m=10.0,
        width_m=8.0,
        height_m=2.8,
    )
    level.add_room(Room("R1", "Living room", 6.0, 5.0, 2.8))
    level.add_room(Room("R2", "Kitchen", 4.0, 3.0, 2.8))
    level.add_room(Room("R3", "Bedroom", 4.0, 3.0, 2.8))

    wall_front = Wall("W1", 10.0, 0.25, 2.8, exterior=True, load_bearing=True)
    wall_front.add_opening(
        Opening(
            kind="window",
            width_m=1.5,
            height_m=1.2,
            sill_height_m=0.9,
            position_m=2.0,
        )
    )
    level.add_wall(wall_front)
    level.add_wall(Wall("W2", 10.0, 0.25, 2.8, exterior=True, load_bearing=True))
    level.add_wall(Wall("W3", 8.0, 0.25, 2.8, exterior=True, load_bearing=True))
    level.add_wall(Wall("W4", 8.0, 0.25, 2.8, exterior=True, load_bearing=True))
    level.add_wall(Wall("W5", 5.0, 0.20, 2.8, load_bearing=False))

    model.add_level(level)
    return model


def test_minimal_renderer_house_is_complete_for_adapter_measurement():
    scene = adapt_building(minimal_renderer_house())
    level = scene["levels"][0]

    assert scene["building"]["name"] == "Renderer Measurement House"
    assert level["id"] == "L1"
    assert len(level["rooms"]) == 3
    assert len(level["walls"]) == 5
    assert len(level["walls"][0]["openings"]) == 1
    assert level["walls"][0]["openings"][0]["width_m"] == 1.5
    assert level["walls"][0]["openings"][0]["height_m"] == 1.2


def test_renderer_poc_must_stop_when_authoritative_spatial_facts_are_absent():
    scene = adapt_building(minimal_renderer_house())
    walls = scene["levels"][0]["walls"]

    for wall in walls:
        assert "x_m" not in wall
        assert "y_m" not in wall
        assert "z_m" not in wall
        assert "rotation_deg" not in wall
