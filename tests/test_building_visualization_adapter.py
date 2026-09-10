from lat_ces.adapters import adapt_building
from lat_ces.building_model import BuildingModel, Level, Opening, Room, Wall


def test_adapter_preserves_building_geometry_and_identity():
    model = BuildingModel(name="POC House")
    level = Level(
        id="ground",
        name="Ground floor",
        length_m=10.0,
        width_m=8.0,
        height_m=2.8,
    )
    room = Room(
        id="living",
        name="Living room",
        length_m=6.0,
        width_m=5.0,
        height_m=2.8,
    )
    wall = Wall(
        id="W1",
        length_m=10.0,
        thickness_m=0.25,
        height_m=2.8,
        exterior=True,
        load_bearing=True,
    )
    wall.add_opening(
        Opening(
            kind="window",
            width_m=1.5,
            height_m=1.2,
            sill_height_m=0.9,
            position_m=2.0,
        )
    )
    level.add_room(room)
    level.add_wall(wall)
    model.add_level(level)

    scene = adapt_building(model)

    assert scene["schema"] == "latces.visualization.scene.v1"
    assert scene["source"] == "BuildingModel"
    assert scene["building"] == {"name": "POC House"}
    assert scene["levels"][0]["id"] == "ground"
    assert scene["levels"][0]["rooms"][0]["id"] == "living"
    assert scene["levels"][0]["rooms"][0]["length_m"] == 6.0
    assert scene["levels"][0]["walls"][0]["id"] == "W1"
    assert scene["levels"][0]["walls"][0]["thickness_m"] == 0.25
    assert scene["levels"][0]["walls"][0]["openings"][0] == {
        "kind": "window",
        "width_m": 1.5,
        "height_m": 1.2,
        "sill_height_m": 0.9,
        "position_m": 2.0,
    }


def test_adapter_does_not_invent_spatial_coordinates():
    model = BuildingModel(name="No Coordinates")
    model.add_level(Level("L1", "Level 1", 4.0, 3.0, 2.7))

    scene = adapt_building(model)

    assert "x_m" not in scene
    assert "y_m" not in scene
    assert "z_m" not in scene
