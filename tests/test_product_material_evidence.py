import pytest

from lat_ces.catalog.product_catalog import get_product


PRODUCT_ID = "MASONRY-THERMAL-25X25X30"


def test_thermal_masonry_product_has_reference_engineering_properties():
    product = get_product(PRODUCT_ID)

    assert product is not None
    assert product.manufacturer == "Wienerberger"
    assert product.density_kg_m3 == pytest.approx(630.0)
    assert product.thermal_conductivity_w_mk == pytest.approx(0.145)
    assert product.compressive_strength_mpa == pytest.approx(10.0)
    assert product.status == "REFERENCE"


def test_thermal_masonry_product_retains_provenance_identity():
    product = get_product(PRODUCT_ID)

    assert product is not None
    assert product.source == "Wienerberger Bosnia official technical sheet"
    assert product.source_uri
    assert product.source_document == "Porotherm 25 S Tehnički list"
    assert product.evidence_id == "EXT-WIENERBERGER-BA-POROTHERM-25S"
    assert product.canonical_product_id == "MASONRY-POROTHERM-25-S"
    assert "independent verification" in product.verification_note
