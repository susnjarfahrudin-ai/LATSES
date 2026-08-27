import pytest

from lat_ces.scientific.core.knowledge_validation_sci0062_0145 import (
    AdaptiveSecurityState,
    ConfidenceScore,
    KnowledgeGraph,
    KnowledgeState,
    OntologyEntity,
    OntologyRelation,
    ReasoningStep,
    ScientificClaim,
    ScientificEvidence,
    ScientificKnowledgeValidationRecord,
    ScientificKnowledgeValidator,
    ScientificMethod,
)


def test_ontology_to_reasoning_chain_is_explicit():
    entities = (
        OntologyEntity("temp", "Temperature", "Thermodynamics", "Thermal state quantity"),
        OntologyEntity("heat", "HeatTransfer", "Thermodynamics", "Energy transfer by heat"),
    )
    graph = KnowledgeGraph(entities=entities, relations=(OntologyRelation("temp", "supports", "heat", "PROV-1"),))
    assert graph.connected("temp", "heat")
    step = ReasoningStep(("temp",), "validated thermal relation", "heat", ("temp", "supports", "heat"))
    assert step.trace[-1] == step.conclusion


def test_validation_requires_evidence_method_and_provenance():
    claim = ScientificClaim("C-0062", "Heat transfer depends on temperature difference", "Thermodynamics")
    evidence = (ScientificEvidence("E-1", "Experimental", "Sensor campaign", "P-1", "VERIFIED"),)
    method = ScientificMethod("M-1", "Calibrated temperature measurement", (("accuracy", "±0.2°C"),), "Limited by sensor uncertainty")
    validator = ScientificKnowledgeValidator()
    assert validator.validate(claim, evidence, method, ("P-1",))
    assert not validator.validate(claim, evidence, method, ())
    assert not validator.validate(claim, (), method, ("P-1",))
    assert not validator.validate(claim, evidence, None, ("P-1",))


def test_invalid_evidence_cannot_validate_claim():
    claim = ScientificClaim("C-1", "x", "Physics")
    evidence = (ScientificEvidence("E-1", "Experimental", "source", "P-1", "FAILED"),)
    method = ScientificMethod("M-1", "procedure", (), "limitation")
    assert not ScientificKnowledgeValidator().validate(claim, evidence, method, ("P-1",))


def test_confidence_is_transparent_and_bounded():
    score = ConfidenceScore(0.8, 0.9, 0.7, 0.6)
    assert score.value() == pytest.approx(0.75)


def test_confidence_rejects_out_of_range_components():
    with pytest.raises(ValueError):
        ConfidenceScore(1.2, 0.9, 0.7, 0.6).value()


def test_sko_validation_record_is_deterministic():
    claim = ScientificClaim("C-1", "x", "Physics")
    evidence = (ScientificEvidence("E-1", "Experimental", "source", "P-1", "VERIFIED"),)
    method = ScientificMethod("M-1", "procedure", (), "limitation")
    record = ScientificKnowledgeValidationRecord(claim, evidence, method, ("P-1",), state=KnowledgeState.VALIDATED, confidence=ConfidenceScore(1, 1, 1, 1))
    assert record.canonical_hash() == record.canonical_hash()
    assert len(record.canonical_hash()) == 64


def test_security_state_keeps_human_oversight_boundary():
    state = AdaptiveSecurityState("LOW", ("AUDIT",), "ROM-1")
    assert state.human_oversight_required is True
