import pytest

from lat_ces.rci_ad.defense_contract import bind_flow_observation_to_defense
from lat_ces.rci_ad.flow_observation import observe_flow
from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
)


def _observation():
    guard = FlowGuard({name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")})
    observed = {name: 100.0 for name in guard.baseline}
    observed["frequency"] = 119.9
    return guard, observe_flow(guard, observed, lambda _: None, timestamp=123.0)


def test_rci_ad_observation_binds_to_unverified_defense_record() -> None:
    guard, observation = _observation()
    defense = AdaptiveDefense()

    record = bind_flow_observation_to_defense(
        defense,
        observation,
        invariant_id="flow:frequency:1199",
        attack_class="flow-anomaly",
        source="A",
    )

    assert record.verified is False
    assert record.verification_sha is None
    assert record.source == "A"
    assert '"kind":"rci-ad-flow-observation"' in record.evidence
    assert '"limiting_dimension":"frequency"' in record.evidence
    assert guard.baseline == {name: 100.0 for name in guard.baseline}
    assert observation.decision.allowed is True


def test_only_verified_rci_ad_evidence_crosses_adaptive_defense_boundary() -> None:
    _, observation = _observation()
    source = AdaptiveDefense()
    standby = AdaptiveDefense()

    record = bind_flow_observation_to_defense(
        source,
        observation,
        invariant_id="flow:frequency:1199",
        attack_class="flow-anomaly",
        source="A",
    )
    source.quarantine(record)

    with pytest.raises(ValueError):
        standby.import_verified(record)

    verified = source.promote(record, verification_sha="verification-abc")
    standby.import_verified(verified)

    assert standby.export_verified() == (verified,)


def test_verified_rci_ad_evidence_is_compatible_with_ab_recovery_contract() -> None:
    _, observation = _observation()
    defense_a = AdaptiveDefense()
    defense_b = AdaptiveDefense()
    record = bind_flow_observation_to_defense(
        defense_a,
        observation,
        invariant_id="flow:frequency:1199",
        attack_class="flow-anomaly",
        source="A",
    )
    verified = defense_a.promote(record, verification_sha="verification-abc")
    defense_b.import_verified(verified)

    checkpoint = RecoveryCheckpoint("rev-1", "hash-1", "verified-baseline")
    machine = RecoveryStateMachine(
        state=RecoveryState.ACTIVE,
        active_role=ExecutionRole.PROCESS,
        recovering_role=ExecutionRole.REVISION_RECOVERY,
        checkpoint=checkpoint,
    )
    takeover = machine.on_failure(HealthState.DEGRADED)
    standby = takeover.activate_standby()
    active_b = standby.promote_standby()

    assert active_b.state is RecoveryState.ACTIVE
    assert active_b.active_role is ExecutionRole.REVISION_RECOVERY
    assert defense_b.export_verified() == (verified,)
