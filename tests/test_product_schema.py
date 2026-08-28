from lat_ces.product_schema import Product


def test_product_schema_has_shared_engineering_fields():
    product = Product(
        id="test-product",
        name="Test product",
        category="construction",
        material="concrete",
        dimensions="1x1x0.2 m",
        mass_kg_per_unit=100.0,
        density_kg_m3=2400.0,
        thermal_conductivity_w_mk=1.7,
        acoustic_rating_db=40.0,
        price=100.0,
        manufacturer="Example",
        source="catalog",
    )

    assert product.id == "test-product"
    assert product.name == "Test product"
    assert product.category == "construction"
    assert product.density_kg_m3 == 2400.0
    assert product.thermal_conductivity_w_mk == 1.7
    assert product.acoustic_rating_db == 40.0


def test_product_schema_allows_unknown_catalog_metadata():
    product = Product(id="minimal", name="Minimal", category="other")
    assert product.material is None
    assert product.dimensions is None
    assert product.manufacturer is None
    assert product.source is None
