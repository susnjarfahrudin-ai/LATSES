from __future__ import annotations

import importlib

from lat_ces.scientific.core import (
    AdaptiveSecurityGovernance,
    ArtifactRegistry,
    AssuranceEngine,
    EcosystemEngine,
    EcosystemNode,
    EvolutionEngine,
    FederationEngine,
    GovernanceEngine,
    IntegrityTrustEngine,
    IntelligenceEngine,
    LifecycleEngine,
    LifecycleState,
    Ontology,
    OntologyEntity,
    PreservationEngine,
    ReasoningEngine,
    SecurityGovernanceEngine,
    ScientificArtifact,
    SynthesisEngine,
)
from lat_ces.scientific.core.building_adapter import to_building_result


def approved_artifact() -> ScientificArtifact:
    artifact = ScientificArtifact(
        artifact_id="ART-001",
        sci_id="LAT-SCI-CORE-0074",
        kind="engineering-result",
        version=1,
        state=LifecycleState.VALIDATED,
        content={"value": 42.0, "unit": "Pa"},
        provenance=("test-source",),
        uncertainty=0.5,
    ).with_hash()
    return artifact


def test_ontology_identity_relations_and_provenance():
    graph = Ontology()
    graph.add_entity(OntologyEntity("building", "object", "building", domain="A building", provenance=("scope",)))
    graph.add_entity(OntologyEntity("room", "object", "building", domain="A room", provenance=("scope",)))
    graph.relate("building", "contains", "room")
    assert graph.validate().relations()[0].relation == "contains"


def test_reasoning_requires_traceability():
    result = ReasoningEngine().infer(
        rule_id="pressure-limit",
        inputs=("measurement-1",),
        output={"safe": True},
        assumptions=("steady-state",),
        provenance=("rulebook-v1",),
        confidence=0.95,
        validated=True,
    )
    assert result.provenance == ("rulebook-v1",)
    assert result.validated is True


def test_synthesis_preserves_lineage_and_uncertainty():
    result = SynthesisEngine().synthesize(
        model_id="hvac-balance",
        inputs=("measurement-1", "measurement-2"),
        output={"flow": 120},
        provenance=("calculation-v1",),
        uncertainty=2.0,
        validated=True,
    )
    assert result.inputs == ("measurement-1", "measurement-2")
    assert result.uncertainty == 2.0


def test_evolution_and_lifecycle_are_controlled():
    artifact = approved_artifact()
    revised = EvolutionEngine().revise(artifact, content={"value": 43.0}, provenance=("revision-1",))
    assert revised.version == 2
    approved = LifecycleEngine().transition(revised, LifecycleState.VALIDATED)
    approved = LifecycleEngine().transition(approved, LifecycleState.APPROVED)
    assert approved.state is LifecycleState.APPROVED


def test_governance_requires_evidence():
    decision = GovernanceEngine().decide(
        artifact_id="ART-001",
        authority="LAT-GOV",
        decision="approve",
        rationale="Verified contract",
        evidence=("ci-run-1",),
    )
    assert decision.evidence == ("ci-run-1",)


def test_preservation_and_integrity_are_reproducible():
    artifact = approved_artifact()
    snapshot = PreservationEngine().snapshot(artifact, retention_class="SCIENTIFIC")
    assert snapshot.snapshot_hash == artifact.content_hash
    assert IntegrityTrustEngine().verify(artifact)


def test_assurance_reports_high_for_validated_trustworthy_artifact():
    result = AssuranceEngine().assess(approved_artifact())
    assert result.level == "HIGH"


def test_ecosystem_registers_and_links_domains():
    engine = EcosystemEngine()
    engine.register(EcosystemNode("core", "engineering", "1", ("validate",)))
    engine.register(EcosystemNode("gui", "presentation", "1", ("render",)))
    engine.link("core", "gui")
    assert ("core", "gui") in engine.links


def test_intelligence_remains_a_recommendation_not_a_fact():
    rec = IntelligenceEngine().recommend(
        rule_id="fan-affinity-check",
        inputs=("fan-curve",),
        recommendation="reduce-speed",
        evidence=("curve-evidence",),
    )
    assert rec.recommendation == "reduce-speed"


def test_federation_requires_integrity_match():
    artifact = approved_artifact()
    engine = FederationEngine()
    envelope = engine.package(artifact, issuer="LATSES", audience="LATCES")
    assert engine.accept(envelope, artifact)


def test_security_policy_rejects_high_risk():
    decision = SecurityGovernanceEngine().evaluate(
        policy_id="default",
        subject="builder",
        action="write-model",
        risk=0.9,
        allowed_actions=frozenset({"write-model"}),
    )
    assert decision.allowed is False


def test_adaptive_security_normalizes_risk():
    value = AdaptiveSecurityGovernance().adjust_risk(baseline=0.4, observed=0.9, threshold=0.8)
    assert value == 1.0


def test_building_boundary_accepts_only_validated_artifacts():
    result = to_building_result(approved_artifact())
    assert result.sci_id == "LAT-SCI-CORE-0074"
    assert result.content_hash


def test_all_canonical_modules_import():
    for module_name in (
        "lat_ces.scientific.core",
        "lat_ces.scientific.core.ontology",
        "lat_ces.scientific.core.reasoning",
        "lat_ces.scientific.core.synthesis",
        "lat_ces.scientific.core.governance",
        "lat_ces.scientific.core.building_adapter",
    ):
        assert importlib.import_module(module_name)


def test_artifact_registry_detects_identity_collisions():
    registry = ArtifactRegistry()
    first = registry.register(approved_artifact())
    assert registry.get(first.artifact_id) == first
    try:
        registry.register(
            ScientificArtifact(
                artifact_id="ART-001",
                sci_id="LAT-SCI-CORE-0074",
                kind="engineering-result",
                version=9,
                state=LifecycleState.VALIDATED,
                content={"value": 99},
                provenance=("other-source",),
            )
        )
    except ValueError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("Artifact identity collision was not rejected")
