"""Adversarial HVAC falsification test for Scientific Sufficiency."""

from lat_ces.scientific.sufficiency import (
    EvidenceState,
    Factor,
    SufficiencyStatus,
    evaluate_sufficiency,
)


def test_hvac_sufficiency_is_revoked_by_relevant_unknown_factor():
    """A nominally sufficient HVAC result must not survive a decision-relevant UNKNOWN."""
    baseline = (
        Factor("room_volume", EvidenceState.VERIFIED, value=60.0, uncertainty=0.0, sensitivity=0.0),
        Factor("design_airflow", EvidenceState.MEASURED, value=30.0, uncertainty=1.0, sensitivity=0.2),
    )

    initially = evaluate_sufficiency(baseline, decision_margin=2.0)
    assert initially.status is SufficiencyStatus.SUFFICIENT
    assert initially.confidence_eligible is True

    adversarial = baseline + (
        # The factor was absent from the initial conclusion. Its allowed
        # uncertainty can consume the complete decision margin.
        Factor("infiltration_air_change", EvidenceState.UNKNOWN, uncertainty=1.0, sensitivity=2.0),
    )

    revised = evaluate_sufficiency(adversarial, decision_margin=2.0)

    assert revised.status is SufficiencyStatus.INSUFFICIENT
    assert revised.confidence_eligible is False
    assert revised.limiting_factor == "infiltration_air_change"
    assert revised.status is not initially.status
