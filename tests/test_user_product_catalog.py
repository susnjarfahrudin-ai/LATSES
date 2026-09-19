from pathlib import Path

from lat_ces.building.model import Material
from lat_ces.catalog.user_store import UserProductCatalog


def _material(product_id: str = "FAKE-001") -> Material:
    return Material(
        name="FAKE materijal",
        category="Zidovi",
        manufacturer="FAKE proizvođač",
        product_id=product_id,
        density=700.0,
        thermal_conductivity=0.15,
    )


def test_user_product_is_persisted_and_reloaded(tmp_path: Path) -> None:
    path = tmp_path / "product_catalog_user.json"
    first = UserProductCatalog(path)
    product = first.add_material(_material())

    second = UserProductCatalog(path)
    loaded = second.all_products()
    assert len(loaded) == 1
    assert loaded[0].product_id == product.product_id
    assert loaded[0].category == "Zidovi"
    assert loaded[0].status == "USER_DECLARED"


def test_user_product_must_use_existing_category(tmp_path: Path) -> None:
    catalog = UserProductCatalog(tmp_path / "catalog.json")
    invalid = Material(
        name="Materijal",
        category="Nova kategorija",
        manufacturer="Proizvođač",
        product_id="INVALID-001",
        density=700.0,
    )
    try:
        catalog.add_material(invalid)
    except ValueError as exc:
        assert "postojećih kategorija" in str(exc)
    else:
        raise AssertionError("Expected category validation failure")


def test_user_product_does_not_overwrite_different_product_id_record(tmp_path: Path) -> None:
    path = tmp_path / "catalog.json"
    catalog = UserProductCatalog(path)
    catalog.add_material(_material())
    try:
        catalog.add_material(
            Material(
                name="Drugi materijal",
                category="Zidovi",
                manufacturer="Drugi proizvođač",
                product_id="FAKE-001",
                density=900.0,
            )
        )
    except ValueError as exc:
        assert "već postoji" in str(exc)
    else:
        raise AssertionError("Expected duplicate product rejection")
