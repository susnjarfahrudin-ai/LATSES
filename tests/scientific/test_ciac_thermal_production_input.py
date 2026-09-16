from types import SimpleNamespace

from lat_ces.catalog.product_catalog import get_product
from lat_ces.scientific.ciac.thermal_production_input import (
    admit_wall_thermal_conductivity,
    material_thermal_conductivity_instance,
    product_thermal_conductivity_instance,
)
from lat_ces.scientific.evidence_state import EvidenceState


def _wall():
    return SimpleNamespace(wall_id="wall-1")


def test_material_lambda_becomes_declared_property_instance_without_invented_verification():
    material = SimpleNamespace(material_id="mat-1", thermal_conductivity=0.42)
    instance = material_thermal_conductivity_instance(_wall(), material)

    assert instance.property_id == "thermal_conductivity"
    assert instance.subject_id == "wall-1"
    assert instance.value == 0.42
    assert instance.unit == "W/mK"
    assert instance.source == "USER_DECLARED"
    assert instance.provenance == "GUI_MATERIAL_ENTRY"
    assert instance.evidence_state is EvidenceState.DECLARED
    assert instance.verification_record_id == ""


def test_material_lambda_is_admitted_without_collapsing_declared_and_verified():
    material = SimpleNamespace(material_id="mat-1", thermal_conductivity=0.42)
    admission = admit_wall_thermal_conductivity(
        _wall(),
        material_thermal_conductivity_instance(_wall(), material),
    )

    assert admission.admission.status == "ACCEPTED_FOR_CALCULATION"
    assert admission.admission.context.subject_id == "wall-1"
    assert admission.admission.context.property_id == "thermal_conductivity"
    assert admission.instance.evidence_state is EvidenceState.DECLARED


def test_invalid_material_lambda_is_rejected_at_production_input_boundary():
    material = SimpleNamespace(material_id="mat-1", thermal_conductivity=0.0)
    admission = admit_wall_thermal_conductivity(
        _wall(),
        material_thermal_conductivity_instance(_wall(), material),
    )

    assert admission.admission.status == "REJECTED"
    assert "finite and positive" in admission.admission.reason


def test_catalog_lambda_preserves_real_catalog_source_and_evidence_identity():
    product = get_product("MASONRY-THERMAL-25X25X30")
    assert product is not None

    instance = product_thermal_conductivity_instance(_wall(), product)

    assert instance is not None
    assert instance.value == product.thermal_conductivity_w_mk
    assert instance.source == product.source
    assert instance.provenance == product.source_document
    assert instance.evidence_id == product.evidence_id
    assert instance.evidence_state is EvidenceState.UNKNOWN


def test_product_catalog_lambda_can_be_admitted_without_claiming_independent_verification():
    product = get_product("MASONRY-THERMAL-25X25X30")
    assert product is not None
    instance = product_thermal_conductivity_instance(_wall(), product)
    assert instance is not None

    admission = admit_wall_thermal_conductivity(_wall(), instance)

    assert admission.admission.status == "ACCEPTED_FOR_CALCULATION"
    assert admission.instance.evidence_state is EvidenceState.UNKNOWN
