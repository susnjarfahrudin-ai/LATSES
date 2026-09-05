from lat_ces.product_catalog_seed import seed_products


def test_seed_catalog_contains_real_products_across_core_domains():
    products = seed_products()
    categories = {product.category for product in products}

    assert len(products) >= 6
    assert {
        "masonry_block",
        "partition_board",
        "acoustic_partition_board",
        "insulation",
        "roof_cover",
        "heat_recovery_ventilation",
    } <= categories


def test_seed_catalog_keeps_manufacturer_source_for_traceability():
    products = seed_products()
    assert all(product.manufacturer for product in products)
    assert all(product.source.startswith("https://") for product in products)


def test_seed_catalog_does_not_invent_missing_engineering_values():
    q350 = next(p for p in seed_products() if p.id == "zehnder-comfoair-q350-tr")
    assert q350.thermal_conductivity_w_mk is None
    assert q350.mass_kg_per_unit is None
