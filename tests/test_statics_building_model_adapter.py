from lat_ces.structural.building_model_adapter import to_static_input
from lat_ces.validation.reference_house import build_reference_house


def test_reference_house_feeds_statics_without_duplicate_wall_identity():
    house = build_reference_house()
    house.validate()

    static = to_static_input(house)
    canonical_ids = {wall.wall_id for wall in house.walls}
    projected_ids = {wall.wall_id for wall in static.walls}

    assert projected_ids == canonical_ids
    assert len(static.walls) == len(house.walls)


def test_statics_reads_product_properties_from_canonical_product_records():
    house = build_reference_house()
    static = to_static_input(house)
    products = {product.product_id: product for product in house.products}

    thermo_wall = next(wall for wall in static.walls if wall.product_id == "masonry:example:thermoblock-25")
    source_product = products[thermo_wall.product_id]

    assert thermo_wall.density_kg_m3 == source_product.density_kg_m3
    assert thermo_wall.compressive_strength_mpa == source_product.compressive_strength_mpa
    assert thermo_wall.thickness_m == 0.25
