from lat_ces.material_interface import get_product, material_catalog
from lat_ces.product_schema import Product


def test_material_catalog_covers_core_building_and_mep_products():
    ids = {item.id for item in material_catalog()}
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


def test_material_catalog_entries_use_shared_product_schema():
    assert all(isinstance(item, Product) for item in material_catalog())
    assert all(item.id and item.name and item.category for item in material_catalog())


def test_gui_selection_resolves_the_same_product_identity_and_data():
    product = get_product("filter_f7")
    assert isinstance(product, Product)
    assert product.id == "filter_f7"
    assert product.name == "F7 filter"
    assert product.category == "air_quality"


def test_unknown_product_selection_returns_none():
    assert get_product("does-not-exist") is None
