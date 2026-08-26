from lat_ces.building_model.core import BuildingModel, Level, Material, Opening, Room, Wall
from lat_ces.building_model.quantities import to_quantity_view


def test_quantities_read_canonical_geometry_and_material_identity():
    product = Material("Thermo Block 25", density_kg_m3=800.0, conductivity_w_mk=0.18, product_id="product:block-25", manufacturer="Example")
    model = BuildingModel(name="Reference House", load_bearing_mode="exterior_only")
    level = Level("ground", "Ground", 10.0, 10.0, 2.70)
    level.add_room(Room("kitchen", "Kuhinja", 3.0, 3.0))
    wall = Wall("wall-1", 4.0, 0.25, 2.70, material=product, exterior=True, load_bearing=True)
    wall.add_opening(Opening("window", 1.2, 1.2, position_m=1.0))
    level.add_wall(wall)
    model.add_level(level)

    view = to_quantity_view(model)

    assert view.rooms[0].room_id == "kitchen"
    assert view.rooms[0].name == "Kuhinja"
    assert view.rooms[0].floor_area_m2 == 9.0
    assert view.rooms[0].volume_m3 == 24.3
    assert view.walls[0].wall_id == "wall-1"
    assert view.walls[0].product_id == "product:block-25"
    assert view.walls[0].gross_area_m2 == 10.8
    assert view.walls[0].opening_area_m2 == 1.44
    assert view.walls[0].net_area_m2 == 9.36
    assert view.walls[0].volume_m3 == 2.34
    assert view.openings[0].wall_id == "wall-1"


def test_quantity_views_are_immutable():
    model = BuildingModel()
    level = Level("ground", "Ground", 10.0, 10.0, 2.70)
    level.add_room(Room("room-1", "Soba 1", 3.0, 4.0))
    model.add_level(level)
    view = to_quantity_view(model)

    try:
        view.rooms[0].name = "other"
    except Exception:
        pass
    else:
        raise AssertionError("quantity views must be immutable")

    assert view.rooms[0].room_id == "room-1"
