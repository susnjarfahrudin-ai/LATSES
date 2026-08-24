import pytest

from lat_ces.scientific.core.ontology import Ontology, OntologyEntity
from lat_ces.scientific.core.reasoning import ReasoningEngine
from lat_ces.scientific.core.synthesis import SynthesisEngine


def test_ontology_requires_explicit_entities_and_non_dangling_relations():
    graph = Ontology(ontology_id="ONTO-TEST")
    graph.add_entity(OntologyEntity("building", "system", "building", "Physical building"))
    graph.add_entity(OntologyEntity("room", "component", "building", "Enclosed space"))
    relation = graph.relate("building", "contains", "room")
    assert relation.source_id == "building"
    assert graph.validate() is graph


def test_ontology_rejects_dangling_relation():
    graph = Ontology()
    graph.add_entity(OntologyEntity("a", "entity", "test", "A"))
    with pytest.raises(ValueError, match="existing source and target"):
        graph.relate("a", "related_to", "missing")


def test_reasoning_requires_provenance_and_bounds_confidence():
    engine = ReasoningEngine()
    result = engine.infer(
        rule_id="RULE-001",
        inputs=("MEAS-001",),
        output="RESULT-001",
        provenance=("MEAS-001",),
        confidence=0.95,
        validated=True,
    )
    assert result.validated is True
    assert result.provenance == ("MEAS-001",)

    with pytest.raises(ValueError, match="confidence"):
        engine.infer(rule_id="RULE-001", inputs=("M",), output="R", provenance=("M",), confidence=1.1)


def test_synthesis_preserves_lineage_and_rejects_negative_uncertainty():
    engine = SynthesisEngine()
    result = engine.synthesize(
        model_id="MODEL-001",
        inputs=("MEAS-001", "REASON-001"),
        output={"value": 42},
        provenance=("MEAS-001", "REASON-001"),
        uncertainty=0.4,
    )
    assert result.inputs == ("MEAS-001", "REASON-001")
    assert result.uncertainty == 0.4

    with pytest.raises(ValueError, match="uncertainty"):
        engine.synthesize(
            model_id="MODEL-001", inputs=("M",), output=42, provenance=("M",), uncertainty=-1
        )
