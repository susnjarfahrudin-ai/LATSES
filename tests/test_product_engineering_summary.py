from lat_ces.building.model import BuildingModel
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.catalog.product_engineering import build_product_engineering_report


def test_unbound_model_has_no_product_engineering_records() -> None:
    model = BuildingModel(name="Empty")
    report = build_product_engineering_report(model)
    assert report.records == ()
    assert report.status == "NO_PRODUCT_BINDINGS"
