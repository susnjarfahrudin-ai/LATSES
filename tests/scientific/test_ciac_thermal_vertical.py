import pytest

from lat_ces.scientific.ciac.thermal_vertical import (
    CalculationContext,
    admit_thermal_conductivity,
    calculate_admitted_wall_heat_loss,
)
from lat_ces.scientific.evidence.property_instance import PropertyInstance


def _instance(**overrides: object) -> PropertyInstance:
    values = {
        "property_id": "thermal_conductivity",
        "subject_id": "MATERIAL-001",
        "value": 0.035,
        "unit": "W/(m*K)",
        "source": "manufacturer-declaration",
        "provenance": "DOC-001",
        "evidence_id": "EVID-001",
    }
    values.update(overrides)
    return PropertyInstance(**values)


def _context(**overrides: object) -> CalculationContext:
    values = {
        "context_id": "THERMAL-WALL-001",
        "property_id": "thermal_conductivity",
        "subject_id": "MATERIAL-001",
        "unit": "W/(m*K)",
        "purpose": "opaque exterior wall transmission heat loss",
    }
    values.update(overrides)
    return CalculationContext(**values)


def test_thermal_property_is_admitted_only_for_matching_context():
    admission = admit_thermal_conductivity(_instance(), _context())

    assert admission.status == "ACCEPTED_FOR_CALCULATION"
    assert admission.property_instance is not None


def test_thermal_property_identity_mismatch_is_rejected():
    admission = admit_thermal_conductivity(
        _instance(property_id="density"),
        _context(),
    )

    assert admission.status == "REJECTED"
    assert admission.reason == "property identity mismatch"


def test_thermal_property_subject_mismatch_is_rejected():
    admission = admit_thermal_conductivity(
        _instance(subject_id="MATERIAL-002"),
        _context(),
    )

    assert admission.status == "REJECTED"
    assert admission.reason == "subject identity mismatch"


def test_thermal_property_unit_mismatch_is_rejected():
    admission = admit_thermal_conductivity(
        _instance(unit="W/m2K"),
        _context(),
    )

    assert admission.status == "REJECTED"
    assert admission.reason == "unit mismatch"


@pytest.mark.parametrize("value", [0, -0.1, float("inf"), float("nan"), True])
def test_invalid_thermal_conductivity_is_rejected(value):
    admission = admit_thermal_conductivity(_instance(value=value), _context())

    assert admission.status == "REJECTED"


def test_admission_does_not_depend_on_verification_as_authority():
    declared = admit_thermal_conductivity(_instance(), _context())

    assert declared.status == "ACCEPTED_FOR_CALCULATION"
    assert declared.property_instance.evidence_state.value == "UNKNOWN"


def test_admitted_property_is_the_cap_input_to_the_formula():
    admission = admit_thermal_conductivity(_instance(value=0.035), _context())

    result = calculate_admitted_wall_heat_loss(
        admission,
        area_m2=10.0,
        thickness_m=0.20,
        delta_t_k=20.0,
        r_si_m2k_w=0.13,
        r_se_m2k_w=0.04,
    )

    expected_u = 1.0 / (0.13 + 0.20 / 0.035 + 0.04)
    assert result.u_value_w_m2k == pytest.approx(expected_u)
    assert result.heat_loss_w == pytest.approx(expected_u * 10.0 * 20.0)
    assert result.property_id == "thermal_conductivity"
    assert result.subject_id == "MATERIAL-001"
    assert result.context_id == "THERMAL-WALL-001"


def test_rejected_property_cannot_reach_cap_formula():
    admission = admit_thermal_conductivity(
        _instance(value=-0.035),
        _context(),
    )

    with pytest.raises(ValueError, match="not admitted"):
        calculate_admitted_wall_heat_loss(
            admission,
            area_m2=10.0,
            thickness_m=0.20,
            delta_t_k=20.0,
            r_si_m2k_w=0.13,
            r_se_m2k_w=0.04,
        )


def test_result_lineage_identifies_property_subject_context_and_formula():
    admission = admit_thermal_conductivity(_instance(), _context())
    result = calculate_admitted_wall_heat_loss(
        admission,
        area_m2=10.0,
        thickness_m=0.20,
        delta_t_k=20.0,
        r_si_m2k_w=0.13,
        r_se_m2k_w=0.04,
    )

    assert result.property_id == admission.property_instance.property_id
    assert result.subject_id == admission.property_instance.subject_id
    assert result.context_id == admission.context.context_id
    assert "lambda" in result.formula
