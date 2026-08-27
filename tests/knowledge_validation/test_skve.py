import pytest

from lat_ces.scientific.knowledge_validation import (
    ConfidenceScore, KnowledgeConflict, KnowledgeState, KnowledgeStateMachine,
    KnowledgeValidator, ScientificClaim, ScientificEvidence,
    ScientificKnowledgeValidationRecord, ScientificMethod,
)


def claim():
    return ScientificClaim("Heat transfer increases with temperature difference", "Thermodynamics", claim_id="CLAIM-THERMO-0001")


def evidence(integrity="VERIFIED", provenance="SDO-TEMP-001"):
    return ScientificEvidence("Experimental", "Temperature sensor", provenance, integrity, evidence_id="EVID-001", measurement_id="MEAS-TEMP-001")


def method():
    return ScientificMethod("METHOD-TEMP-001", "Calibrated temperature measurement", {"accuracy": 0.2, "calibration": "CAL-001"}, "Uncertainty recorded")


def confidence(v=0.9):
    return ConfidenceScore(v, v, v, v)


def test_skv_t001_claim_identity_creation():
    assert claim().claim_id


def test_skv_t002_claim_statement_preservation():
    assert claim().statement == "Heat transfer increases with temperature difference"


def test_skv_t003_domain_classification():
    assert claim().domain == "Thermodynamics"


def test_skv_t004_evidence_required_for_validation():
    result = KnowledgeValidator().validate(claim(), [], method(), confidence())
    assert not result.valid and result.state == KnowledgeState.HYPOTHESIS


def test_skv_t005_evidence_integrity_and_provenance_fields():
    e = evidence()
    assert e.evidence_id and e.source and e.provenance_id and e.integrity_status


def test_skv_t006_invalid_evidence_rejected():
    assert not KnowledgeValidator().validate(claim(), [evidence("FAILED")], method(), confidence()).valid


def test_skv_t007_method_presence_required():
    assert not KnowledgeValidator().validate(claim(), [evidence()], None, confidence()).valid


def test_skv_t008_method_parameter_preservation():
    m = method()
    assert m.parameters["accuracy"] == 0.2
    with pytest.raises(TypeError):
        m.parameters["accuracy"] = 0.1


def test_skv_t009_method_limitation_recording():
    assert method().limitations == "Uncertainty recorded"


def test_skv_t010_initial_knowledge_state():
    assert claim().status == KnowledgeState.UNKNOWN


def test_skv_t011_valid_state_transition_chain():
    machine = KnowledgeStateMachine()
    for state in (KnowledgeState.HYPOTHESIS, KnowledgeState.SUPPORTED, KnowledgeState.VALIDATED, KnowledgeState.CONFIRMED):
        machine.transition(state)
    assert machine.state == KnowledgeState.CONFIRMED


def test_skv_t012_invalid_state_transition_detected():
    with pytest.raises(ValueError):
        KnowledgeStateMachine().transition(KnowledgeState.CONFIRMED)


def test_skv_t013_confidence_calculation():
    assert confidence().calculate() == pytest.approx(0.9)


def test_skv_t014_confidence_transparency():
    assert set(confidence().as_components()) == {"evidence_score", "method_score", "provenance_score", "reference_score"}


def test_skv_t015_confidence_boundary():
    ConfidenceScore(0, 1, 0, 1)
    with pytest.raises(ValueError):
        ConfidenceScore(-0.1, 0.5, 0.5, 0.5)
    with pytest.raises(ValueError):
        ConfidenceScore(0.5, 0.5, 0.5, 1.1)


def test_skv_t016_conflict_record_creation():
    assert KnowledgeConflict("CLAIM-A", "CLAIM-B", "EVID-A", "EVID-B", "OPEN").conflict_id


def test_skv_t017_conflict_preservation():
    record = ScientificKnowledgeValidationRecord(claim(), (evidence(),), method(), ("SDO-TEMP-001",), KnowledgeState.VALIDATED, confidence())
    updated = record.with_conflict(KnowledgeConflict("CLAIM-A", "CLAIM-B", "EVID-A", "EVID-B", "OPEN"))
    assert len(updated.conflicts) == 1


def test_skv_t018_complete_validation_chain():
    result = KnowledgeValidator().validate(claim(), [evidence()], method(), confidence())
    assert result.valid and result.state == KnowledgeState.VALIDATED


def test_skv_t019_missing_provenance_rejected():
    bad = ScientificEvidence("Experimental", "Sensor", "", "VERIFIED", evidence_id="EVID-002")
    assert not KnowledgeValidator().validate(claim(), [bad], method(), confidence()).valid


def test_skv_t020_weak_evidence_cannot_be_confirmed():
    result = KnowledgeValidator().validate(claim(), [evidence()], method(), confidence(0.7), KnowledgeState.CONFIRMED)
    assert not result.valid and result.state == KnowledgeState.VALIDATED


def test_skv_t021_sko_validation_attachment():
    record = ScientificKnowledgeValidationRecord(claim(), (evidence(),), method(), ("SDO-TEMP-001",), KnowledgeState.VALIDATED, confidence())
    assert record.validation_state == KnowledgeState.VALIDATED


def test_skv_t022_sko_history_preservation():
    record = ScientificKnowledgeValidationRecord(claim(), (evidence(),), method(), ("SDO-TEMP-001",), KnowledgeState.SUPPORTED, confidence(), (KnowledgeState.HYPOTHESIS, KnowledgeState.SUPPORTED))
    updated = record.with_state(KnowledgeState.VALIDATED)
    assert updated.revision_history == (KnowledgeState.HYPOTHESIS, KnowledgeState.SUPPORTED, KnowledgeState.VALIDATED)


def test_skv_t023_complete_scientific_knowledge_trace():
    e = evidence()
    record = ScientificKnowledgeValidationRecord(claim(), (e,), method(), (e.provenance_id,), KnowledgeState.VALIDATED, confidence())
    assert record.claim.claim_id and record.evidence[0].measurement_id and record.provenance_ids[0] and record.method.method_id
