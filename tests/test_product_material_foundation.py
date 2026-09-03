from lat_ces.catalog import (
    ProductIdentity,
    ProductProperty,
    ProductRecord,
    ProductRegistry,
    StandardReference,
    StandardsRegistry,
)


def test_product_identity_and_registry_preserve_manufacturer_product_link():
    product = ProductRecord(
        identity=ProductIdentity(
            product_id="masonry:example:thermoblock-25",
            category="masonry_block",
            manufacturer="Example Manufacturer",
            product_name="Thermo Block 25",
            product_uri="https://example.invalid/products/thermoblock-25",
        ),
        properties=(
            ProductProperty("thermal_conductivity", "0.18", "W/mK"),
            ProductProperty("compressive_strength", "10", "MPa"),
        ),
        dimensions_m=(0.25, 0.25, 0.30),
        dataset_id="example-catalog",
        dataset_version="1",
    )

    registry = ProductRegistry()
    registry.add(product)

    assert registry.get(product.identity.product_id) == product
    assert registry.list_category("masonry_block") == (product,)
    assert product.property("thermal_conductivity").unit == "W/mK"


def test_standards_registry_is_versioned_and_element_scoped():
    registry = StandardsRegistry()
    iso = StandardReference(
        organization="ISO",
        designation="6946",
        edition="2017",
        scope="thermal resistance and transmittance",
        applicable_to=("wall", "roof", "floor"),
    )
    registry.add(iso)

    assert registry.get("ISO:6946:2017") == iso
    assert registry.for_element("wall") == (iso,)
    assert registry.for_element("window") == ()
