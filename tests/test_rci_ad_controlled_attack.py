"""Controlled RCI-AD attack matrix derived from the canonical architecture specification.

This suite exercises implemented security primitives directly and marks
missing architectural boundaries as strict expected failures.
"""

from __future__ import annotations

import hashlib
import json
import math

import pytest

from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.rate_limit import TokenBucketRateLimiter
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel
from lat_ces.security.threat_score import ThreatScoreEngine, ThreatScorePolicy


BASELINE = {
    "frequency": 100.0,
    "volume": 100.0,
    "concurrency": 10.0,
    "novelty": 1.0,
}


def test_controlled_attack_matrix_existing_defenses() -> None:
    """Normal -> throttle -> hard stop -> replay -> tamper -> rate -> block."""

    guard = FlowGuard(BASELINE)
    assert guard.evaluate(BASELINE).allowed is True

    throttled = guard.evaluate({**BASELINE, "frequency": 115.0})
    assert throttled.allowed is True
    assert 0.0 < throttled.throttle < 1.0
    assert throttled.limiting_dimension == "frequency"

    stopped = guard.evaluate({**BASELINE, "frequency": 120.0})
    assert stopped.allowed is False
    assert stopped.throttle == 0.0
    assert stopped.max_deviation >= 0.20

    channel = SignedIPCChannel(b"controlled-attack-secret")
    limiter = TokenBucketRateLimiter(capacity=2.0, refill_per_second=1.0)
    threat = ThreatScoreEngine(ThreatScorePolicy(block_threshold=50.0))
    defense = AdaptiveDefense()
    fortress = CyberFortress(
        channel,
        rate_limiter=limiter,
        threat_engine=threat,
        adaptive_defense=defense,
    )

    packet = channel.pack({"operation": "probe"}, sender_id="controlled-test")
    assert fortress.receive("10.10.10.10", packet, now=100.0) == {"operation": "probe"}

    with pytest.raises(SecurityError, match="replay"):
        fortress.receive("10.10.10.10", packet, now=100.0)

    rate_packet_1 = channel.pack(
        {"operation": "rate-probe-1"}, sender_id="controlled-test"
    )
    rate_packet_2 = channel.pack(
        {"operation": "rate-probe-2"}, sender_id="controlled-test"
    )
    assert fortress.receive("10.10.10.11", rate_packet_1, now=100.0) == {
        "operation": "rate-probe-1"
    }
    assert fortress.receive("10.10.10.11", rate_packet_2, now=100.0) == {
        "operation": "rate-probe-2"
    }

    rate_packet_3 = channel.pack(
        {"operation": "rate-probe-3"}, sender_id="controlled-test"
    )
    with pytest.raises(SecurityError, match="rate-limited"):
        fortress.receive("10.10.10.11", rate_packet_3, now=100.0)

    forged = json.loads(
        channel.pack({"operation": "tamper"}, sender_id="controlled-test").decode()
    )
    forged["mac"] = "0" * 64
    forged_packet = json.dumps(forged, separators=(",", ":")).encode()

    with pytest.raises(SecurityError, match="IPC authentication failed"):
        fortress.receive("10.10.10.12", forged_packet, now=101.0)

    assert threat.score("10.10.10.12", now=101.0) >= 25.0
    assert defense.records()[0].attack_class == "ipc-rejection"

    threat.record("10.10.10.13", 50.0, now=100.0)
    with pytest.raises(SecurityError, match="threat-blocked"):
        fortress.receive(
            "10.10.10.13",
            channel.pack({"operation": "blocked"}, sender_id="controlled-test"),
            now=100.0,
        )

    failure = defense.observe_failure(
        "controlled:resource-pressure",
        "resource-pressure",
        "predicted resource budget exceeded",
        source="controlled-attack-test",
    )
    assert defense.is_quarantined(failure.invariant_id) is False

    with pytest.raises(ValueError):
        defense.import_verified(failure)

    verified = defense.promote(
        failure,
        verification_sha="controlled-test-verification",
    )
    assert verified.verified is True
    assert defense.is_quarantined(verified.invariant_id) is True


def test_slow_drip_attack_cannot_poison_flow_baseline() -> None:
    """Gradual pressure cannot redefine the trusted baseline."""

    guard = FlowGuard(BASELINE)
    trusted_baseline = guard.baseline

    for step in range(13):
        sample = 100.0 * (1.02**step)
        decision = guard.evaluate({**BASELINE, "frequency": sample})

    assert decision.allowed is False
    assert decision.throttle == 0.0
    assert guard.baseline == trusted_baseline


def test_controlled_packet_cost_model_is_fail_closed() -> None:
    """Reference packet-cost rule from the canonical architecture."""

    available = 64.0
    packet_size = 40.0
    amplification = 2.0
    overhead = 8.0
    estimated_cost = amplification * packet_size + overhead

    assert math.isfinite(estimated_cost)
    assert estimated_cost > available


@pytest.mark.xfail(
    strict=True,
    reason="Canonical host-wide Resource Intelligence / Prediction Engine is not yet a production module.",
)
def test_rci_ad_predictive_resource_guard_must_reject_exhaustion() -> None:
    from lat_ces.rci_ad.resource_intelligence import ResourceIntelligence  # type: ignore

    model = ResourceIntelligence()
    result = model.predict_resource_feasibility(
        used=900.0, safe_budget=1000.0, incoming_memory=200.0, horizon=1.0
    )
    assert result.action == "SIGNAL_DEFENSE"


@pytest.mark.xfail(
    strict=True,
    reason="Canonical Universal I/O / Data-Carrier boundary is not yet a production module.",
)
def test_rci_ad_universal_io_must_cover_non_network_carriers() -> None:
    from lat_ces.rci_ad.io_intelligence import UniversalIOObservation  # type: ignore

    carriers = {
        "USB", "BLUETOOTH", "CD", "BLU_RAY", "SD", "NVME", "SATA",
        "THUNDERBOLT", "PCIE", "ETHERNET", "WIFI", "OPTICAL",
    }
    observation = UniversalIOObservation.from_carriers(carriers)
    assert carriers <= set(observation.supported_carriers)


@pytest.mark.xfail(
    strict=True,
    reason="Canonical RCI-AD Communicator boundary is not yet a production module.",
)
def test_rci_ad_communicator_must_route_read_only_canonical_telemetry() -> None:
    from lat_ces.rci_ad.communicator import Communicator  # type: ignore

    communicator = Communicator()
    routed = communicator.route_read_only(
        source="resource-intelligence",
        payload={"resource": "CRITICAL"},
        destination="defense-controller",
    )
    assert routed.read_only is True
    assert routed.destination == "defense-controller"


@pytest.mark.xfail(
    strict=True,
    reason="Canonical RCI-AD Defense Controller boundary is not yet a production module.",
)
def test_rci_ad_defense_controller_must_separate_decision_from_enforcement() -> None:
    from lat_ces.rci_ad.defense_controller import DefenseController  # type: ignore

    controller = DefenseController()
    decision = controller.assess_and_decide(
        resource_pressure="CRITICAL",
        packet_cost="EXCESSIVE",
        integrity="VERIFIED",
        trust="TRUSTED",
    )
    assert decision.action in {"DROP", "ISOLATE"}
    assert controller.enforce(decision).decision_id == decision.decision_id


@pytest.mark.xfail(
    strict=True,
    reason="Canonical Root-of-Trust model verification boundary is not yet a production module.",
)
def test_rci_ad_root_of_trust_must_verify_model_identity_and_vectors() -> None:
    from lat_ces.rci_ad.root_of_trust import RootOfTrust  # type: ignore

    model_bytes = b"canonical-rci-ad-model"
    model_hash = hashlib.sha256(model_bytes).hexdigest()
    trust = RootOfTrust()
    assert trust.verify_model(
        model_bytes,
        expected_hash=model_hash,
        test_vectors=[{"input": 1.0, "expected": 1.0}],
    )


@pytest.mark.xfail(
    strict=True,
    reason="Canonical RCI-AD recovery boundary is not yet a production module.",
)
def test_rci_ad_recovery_must_restore_from_verified_artifact() -> None:
    from lat_ces.rci_ad.recovery import RecoveryController  # type: ignore

    recovery = RecoveryController()
    result = recovery.recover(
        module_id="controlled-test-module",
        trusted_artifact="known-good-artifact",
    )
    assert result.sequence == (
        "DETECT",
        "REVOKE",
        "ISOLATE",
        "RESTORE_FROM_TRUSTED_ARTIFACT",
        "VERIFY",
        "REINTEGRATE",
    )
