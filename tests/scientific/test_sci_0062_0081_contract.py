import pytest

from lat_ces.scientific.ontology import (
    ScientificDefinition,
    ScientificDomain,
    ScientificEntity,
    ScientificRelation,
    OntologyGraph,
    validate_graph,
)
from lat_ces.scientific.reasoning import (
    ScientificKnowledgeReasoningEngine,
    ScientificRule,
    calculate_confidence,
)
from lat_ces.scientific.synthesis import (
    ScientificKnowledgeSynthesisEngine,
    SynthesisMethod,
    calculate_synthesis_confidence,
)
from lat_ces.scientific.evolution import (
    ChangeDetector,
    KnowledgeMigration,
    KnowledgeVersionGraph,
    ScientificKnowledgeEvolutionEngine,
    update_confidence,
)
from lat_ces.scientific.governance import (
    Authority,
    AuditRecord,
    GovernanceRule,
    PolicyEngine,
    ScientificKnowledgeGovernanceEngine,
)
from lat_ces.scientific.core.canonical_sko import ScientificKnowledgeObject


def test_ontology_contract_and_graph():
    domain = ScientificDomain("Thermodynamics", "Science of heat and energy")
    entity = ScientificEntity("Temperature", "Physical Quantity", "Thermal state", domain=domain.name, provenance=("P-1",))
    target = ScientificEntity("Kelvin", "Unit", "SI temperature unit", domain=domain.name, provenance=("P-1",))
    definition = ScientificDefinition("Thermal state measure", "REF-T-1", "1")
    relation = ScientificRelation(entity.entity_id, "USES_UNIT", target.entity_id)
    assert definition.reference == "REF-T-1"
    graph = OntologyGraph()
    graph.add_entity(entity)
    graph.add_entity(target)
    graph.add_relation(ScientificRelation(entity.entity_id, "MEASURED_BY", target.entity_id))
    assert validate_graph(graph)
    with pytest.raises(ValueError):
        OntologyGraph().add_relation(relation)


def test_ontology_rejects_unknown_relation():
    with pytest.raises(ValueError):
        ScientificRelation("A", "UNKNOWN", "B")


def test_reasoning_requires_rule_premises_and_trace():
    engine = ScientificKnowledgeReasoningEngine()
    rule = ScientificRule("RULE-1", "Energy Conservation", "Thermodynamics", "Energy balance")
    engine.register_rule(rule)
    result = engine.reason("RULE-1", ("P-1", "P-2"), "C-1", confidence_values=(0.95, 0.90), trace=("P-1", "RULE-1", "P-2", "C-1"))
    assert result.conclusion == "C-1"
    assert result.confidence == 0.90
    with pytest.raises(ValueError):
        engine.reason("RULE-1", (), "C-2", trace=("C-2",))


def test_reasoning_confidence_is_bounded_minimum():
    assert calculate_confidence((0.95, 0.8, 0.9)) == 0.8
    with pytest.raises(ValueError):
        calculate_confidence((1.1,))


def test_synthesis_requires_inputs_and_method():
    engine = ScientificKnowledgeSynthesisEngine()
    engine.register_method(SynthesisMethod("M-1", "Engineering Synthesis", "Engineering", "Compose validated models"))
    result = engine.synthesize("M-1", ("K-1", "K-2"), output="HVAC Model", confidence_values=(0.95, 0.80), trace=("K-1", "K-2", "M-1", "HVAC Model"))
    assert result.generated_structure == "HVAC Model"
    assert result.confidence == 0.80


def test_synthesis_confidence_never_exceeds_inputs():
    assert calculate_synthesis_confidence((0.95, 0.80)) == 0.80
    with pytest.raises(ValueError):
        calculate_synthesis_confidence((1.2,))


def test_evolution_keeps_history_and_requires_evidence():
    graph = KnowledgeVersionGraph()
    graph.add_version("v1")
    graph.add_version("v2", "v1")
    assert graph.parent_of("v2") == "v1"
    engine = ScientificKnowledgeEvolutionEngine()
    record = engine.evolve("v1", "new measurement", "v2", "improved accuracy", 0.9, evidence=("E-1",))
    assert record.previous_knowledge == "v1"
    with pytest.raises(ValueError):
        engine.evolve("v2", "event", "v3", "reason", 0.9, evidence=())


def test_evolution_change_migration_and_confidence():
    assert ChangeDetector().compare("a", "a")["changed"] is False
    assert ChangeDetector().compare("a", "b")["changed"] is True
    assert KnowledgeMigration().migrate("v1", "v2")["status"] == "MIGRATED"
    assert update_confidence(0.8, 0.1) == 0.9


def test_governance_contracts():
    rule = GovernanceRule("RULE-SKGE-001", "Every change requires evidence", "1.0", "LAT", "ACTIVE")
    authority = Authority("Engineer-A", 2, "Model Modification")
    audit = AuditRecord("CHANGE", authority.identity, "SKO-1", "new evidence", "RECORDED")
    engine = ScientificKnowledgeGovernanceEngine()
    engine.register_rule(rule)
    assert engine.evaluate_change("proposal")["status"] == "UNDER_REVIEW"
    assert PolicyEngine().check("CHANGE", (rule,)) is True
    assert audit.actor == "Engineer-A"


def test_governance_rejects_invalid_authority():
    with pytest.raises(ValueError):
        Authority("", 9, "")


def test_canonical_sko_has_traceable_sections_and_hash():
    sko = ScientificKnowledgeObject(
        name="Thermal Knowledge",
        object_type="ScientificKnowledge",
        definition="Validated thermal relation",
        claim="Heat flow depends on temperature difference",
        evidence=("E-1",),
        provenance=("P-1",),
        validation="VALIDATED",
        ontology="Temperature -> HeatTransfer",
        reasoning="R-1",
        synthesis="S-1",
        evolution=("EV-1",),
        governance=("G-1",),
        preservation=("PR-1",),
        trust="HIGH",
        assurance="HIGH",
        lifecycle="ACTIVE",
    )
    digest = sko.calculate_hash()
    assert len(digest) == 64
    assert sko.sko_id
