from lat_ces.building.model import BuildingModel, Material
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.catalog.product_catalog import get_product
from lat_ces.catalog.product_engineering import build_product_engineering_report
from lat_ces.reference_house_workflow import build_reference_house_workflow


def _attach_catalog_product(model: BuildingModel, product) -> Material:
    material = Material(
        name=product.name,
        density=product.density_kg_m3,
        youngs_modulus=product.youngs_modulus_pa,
        thermal_conductivity=product.thermal_conductivity_w_mk,
        compressive_strength_mpa=product.compressive_strength_mpa,
        product_id=product.product_id,
        manufacturer=product.manufacturer,
        category=product.category,
    )
    model.add_material(material)
    return material


def test_reference_product_feeds_structural_and_thermal_summary() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model
    level = next(iter(model.levels.values()))
    wall = next(iter(level.floor_plan.walls.values()))
    wall.load_bearing = True
    wall.tributary_width_m = 2.5

    product = get_product("CONCRETE-REFERENCE-C25-30")
    assert product is not None
    material = _attach_catalog_product(model, product)
    wall.material_id = material.material_id
    ensure_product_binding_registry(model).bind(wall.wall_id, "wall", product.product_id)

    report = build_product_engineering_report(model)
    record = next(item for item in report.records if item.target_id == wall.wall_id)

    assert record.product_id == "CONCRETE-REFERENCE-C25-30"
    assert record.density_kg_m3 == 2500.0
    assert record.thermal_conductivity_w_mk == 2.10
    assert record.structural_status == "CALCULATED"
    assert record.self_weight_kn_m is not None and record.self_weight_kn_m > 0.0
    assert record.thermal_status == "CALCULATED"
    assert record.conductive_resistance_m2kw == round(wall.thickness / 2.10, 6)
    assert record.source == "LAT-CES reference engineering data"
    assert record.verification_status == "REFERENCE"


def test_missing_product_data_remains_input_required() -> None:
    workflow = build_reference_house_workflow()
    model = workflow.model
    level = next(iter(model.levels.values()))
    wall = next(iter(level.floor_plan.walls.values()))
    wall.load_bearing = True
    wall.tributary_width_m = 2.5
    wall.material_id = None
    ensure_product_binding_registry(model).bind(wall.wall_id, "wall", "MASONRY-THERMAL-25X25X30")

    report = build_product_engineering_report(model)
    record = next(item for item in report.records if item.target_id == wall.wall_id)

    assert record.verification_status == "MISSING"
    assert record.thermal_status == "INPUT_REQUIRED"
    assert record.structural_status == "INPUT_REQUIRED"
    assert "nije odabran materijal" in record.findings or "nedostaje gustina materijala" in record.findings
    assert "nedostaje λ (toplotna provodljivost)" in record.findings
    assert report.status == "INPUT_REQUIRED"


def test_unbound_model_has_no_product_engineering_records() -> None:
    model = BuildingModel(name="Empty")
    report = build_product_engineering_report(model)
    assert report.records == ()
    assert report.status == "NO_PRODUCT_BINDINGS"
