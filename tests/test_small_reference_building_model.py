from lat_ces.building_model import make_small_reference_house


def test_small_reference_house_is_one_consistent_model():
    model = make_small_reference_house()
    level = model.levels["L0"]

    assert model.name == "LATCES Small Reference House"
    assert (level.length_m, level.width_m, level.height_m) == (10.0, 8.0, 2.80)
    assert len(level.rooms) == 4
    assert len(level.walls) == 5
    assert model.total_volume_m3() == 448.0

    door = level.walls["W-S"].openings[0]
    assert (door.width_m, door.height_m) == (0.90, 2.10)
    assert door.z_bottom_m == 0.0
    assert door.z_top_m == 2.10
    assert level.walls["W-S"].solid_vertical_segments() == [(2.10, 2.80)]

    window = level.walls["W-S"].openings[1]
    assert window.sill_height_m == 0.90
    assert window.z_top_m == 2.10


def test_small_reference_house_has_material_provenance_for_walls():
    model = make_small_reference_house()
    level = model.levels["L0"]
    assert level.walls["W-S"].material is model.materials["brick"]
    assert level.walls["W-P1"].material is model.materials["reinforced concrete"]
