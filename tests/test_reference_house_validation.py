import json

from lat_ces.validation.reference_house import build_reference_house


def test_reference_house_is_physically_valid():
    house = build_reference_house()
    house.validate()
    assert {room.name for room in house.rooms} == {"Hodnik", "Kuhinja", "Dnevni boravak", "Soba 1", "Soba 2"}
    assert any(wall.exterior and wall.load_bearing for wall in house.walls)
    assert any(not wall.exterior and not wall.load_bearing for wall in house.walls)
    assert any(opening.kind == "door" for opening in house.openings)
    assert any(opening.kind == "window" for opening in house.openings)
    assert house.stairs and house.terraces


def test_reference_house_serialization_is_deterministic():
    first = build_reference_house()
    second = build_reference_house()
    first.validate()
    second.validate()
    assert first.serialize() == second.serialize()
    reconstructed = json.loads(first.serialize())
    assert reconstructed["name"] == "Reference House"
    assert reconstructed["load_bearing_mode"] == "exterior_only"


def test_reference_house_preserves_product_and_material_identity():
    house = build_reference_house()
    house.validate()
    products = {product.product_id: product for product in house.products}
    wall_products = {wall.product_id for wall in house.walls}
    assert wall_products <= products.keys()
    thermo = products["masonry:example:thermoblock-25"]
    assert thermo.dimensions_m == (.25, .25, .30)
    assert thermo.thermal_conductivity_w_mk == .18
    assert thermo.density_kg_m3 == 800.0
    assert thermo.compressive_strength_mpa == 10.0
