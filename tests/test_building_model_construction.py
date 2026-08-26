from lat_ces.building_model.core import BuildingModel, Ceiling, Level, Material, Opening, Room, Stair, Terrace, Wall


def test_room_name_and_level_height_are_part_of_model():
    level = Level("ground", "Ground", 10, 10, 2.8)
    room = Room("r1", "Kuhinja", 4, 3)
    level.add_room(room)
    assert room.name == "Kuhinja"
    assert room.height_m == 2.8
    assert room.floor_area_m2 == 12


def test_suspended_ceiling_overrides_level_height():
    level = Level("ground", "Ground", 10, 10, 2.8)
    room = Room("r1", "Dnevna", 5, 4, ceiling=Ceiling(True, 2.55))
    level.add_room(room)
    assert room.height_m == 2.55


def test_wall_has_load_bearing_mode_and_product_link():
    material = Material("Thermo block", 800, 0.18, 10, "masonry:example:25", "Example")
    wall = Wall("w1", 5, 0.25, 2.8, material, exterior=True, load_bearing=True)
    wall.add_opening(Opening("door", 0.9, 2.1, position_m=1.0))
    assert wall.load_bearing and not wall.partition
    assert wall.material.product_id == "masonry:example:25"


def test_building_model_supports_both_load_bearing_policies():
    assert BuildingModel(load_bearing_mode="all_walls").load_bearing_mode == "all_walls"
    assert BuildingModel(load_bearing_mode="exterior_only").load_bearing_mode == "exterior_only"


def test_stair_and_terrace_are_first_class_level_elements():
    level = Level("ground", "Ground", 10, 10, 2.8)
    level.add_stair(Stair("s1", 3, 1.1, 16, 0.175, 0.28, True, True, True))
    level.add_terrace(Terrace("t1", 6, 3, "concrete"))
    assert level.stairs["s1"].riser_count == 16
    assert level.terraces["t1"].construction_type == "concrete"
