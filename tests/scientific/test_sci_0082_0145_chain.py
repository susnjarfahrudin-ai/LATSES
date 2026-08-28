from lat_ces.scientific.preservation import ScientificKnowledgePreservationEngine, PreservationMigration, RecoveryManager
from lat_ces.scientific.trust import ScientificKnowledgeTrustEngine
from lat_ces.scientific.assurance import AssuranceCriteria, ScientificKnowledgeAssuranceEngine
from lat_ces.scientific.lifecycle import ScientificKnowledgeLifecycleEngine, LifecycleTransitionEngine
from lat_ces.scientific.ecosystem import EcosystemNode, EcosystemRelationship, ScientificKnowledgeEcosystemEngine
from lat_ces.scientific.intelligence import InputValidationHardening, KnowledgeGrounding, ConfidenceCalibration, SafeMode
from lat_ces.scientific.security import FederationSecurityEngine, SecurityHardeningEngine, SecurityHardeningGovernanceEngine, AdaptiveSecurityGovernance
from lat_ces.scientific.federation import GovernanceFederationEngine


def test_preservation_archive_version_recovery():
    engine = ScientificKnowledgePreservationEngine()
    record = engine.preserve("SKO-1", {"x": 1}, version="1", source="TEST")
    assert record.preservation_id
    assert engine.versions.history("SKO-1")
    assert PreservationMigration().migrate("json-v1", "json-v2")["status"] == "MIGRATED"
    assert RecoveryManager().recover("BACKUP-1")["state"] == "RECOVERED"


def test_trust_and_assurance_require_bounded_inputs():
    assessment = ScientificKnowledgeTrustEngine().assess("SKO-1", evidence=0.95, validation=0.9, provenance=1.0, governance=1.0, reproducibility=0.85)
    assert assessment.trust_score == 0.94
    assured = ScientificKnowledgeAssuranceEngine().assess("SKO-1", AssuranceCriteria(True, True, assessment.trust_score, True, True))
    assert assured.level == "ASSURED"


def test_lifecycle_records_timeline():
    obj = ScientificKnowledgeLifecycleEngine().create("SKO-1")
    engine = LifecycleTransitionEngine()
    obj = engine.transition(obj, "DOCUMENTED", "2026-08-27T00:00:00Z")
    obj = engine.transition(obj, "VALIDATED", "2026-08-27T00:01:00Z")
    assert [event.state for event in obj.history] == ["DOCUMENTED", "VALIDATED"]


def test_ecosystem_relationships_are_explicit():
    engine = ScientificKnowledgeEcosystemEngine()
    eco = engine.create()
    nodes = (EcosystemNode("A", "KNOWLEDGE", "SKO-A", "1"), EcosystemNode("B", "EVIDENCE", "E-1", "1"))
    rels = (EcosystemRelationship("A", "SUPPORTED_BY", "B", ("P-1",)),)
    connected = engine.connect(eco, nodes=nodes, relationships=rels)
    assert connected.state == "CONNECTED"


def test_intelligence_hardening_and_safe_mode():
    assert InputValidationHardening().validate(None, (), "").safe_mode is True
    assert KnowledgeGrounding().require_grounding(("E-1",), "SRC-1", ("R-1",), 0.8).status == "GROUNDED"
    assert ConfidenceCalibration().calibrate(0.95, 0.8) == 0.8
    assert SafeMode().require_human_review("conflict").safe_mode is True


def test_federation_security_and_adaptive_governance():
    payload = {"artifact": "SKO-1", "revision": 1}
    fed = GovernanceFederationEngine().package("SKO-1", payload, issuer="NODE-A", audience="NODE-B")
    assert GovernanceFederationEngine().verify(fed, payload)
    sec = FederationSecurityEngine().seal("SKO-1", payload, "NODE-A")
    assert FederationSecurityEngine().verify(sec, payload)
    assert SecurityHardeningEngine().protect(identity_valid=True, integrity_valid=True, audit_valid=True, recovery_available=True).status == "PROTECTED"
    assert SecurityHardeningGovernanceEngine().evaluate("SECURITY-POLICY", "ENGINEER", "HIGH").status == "GOVERNANCE_REVIEW"
    assert AdaptiveSecurityGovernance().evaluate(False, "HIGH", True).human_oversight_required is True
