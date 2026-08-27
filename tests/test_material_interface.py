from lat_ces.material_interface import material_catalog


def test_material_catalog_covers_core_building_and_mep_products():
    ids = {item[0] for item in material_catalog()}
    required = {
        "floor_slab",
        "masonry_block",
        "partition_block",
        "insulation",
        "floor_finish",
        "roof_cover",
        "roof_beam",
        "ventilation_fan",
        "heat_recovery_unit",
        "duct",
        "duct_elbow",
        "plenum",
        "filter_g4",
        "filter_f7",
    }
    assert required <= ids


def test_material_catalog_entries_have_stable_id_name_and_category():
    assert all(len(item) == 3 and all(item) for item in material_catalog())
