"""Canonical evidence contract from RCI-AD observations to AdaptiveDefense.

RCI-AD observes; AdaptiveDefense owns defense knowledge and verification;
A/B owns execution and recovery. This module is the narrow typed seam between
those responsibilities. It never changes FlowGuard decisions and never grants
RCI-AD authority to verify, promote, or transfer runtime state.
"""
from __future__ import annotations

import hashlib
import json
from typing import Mapping

from lat_ces.security.adaptive_defense import AdaptiveDefense, DefenseRecord
from lat_ces.rci_ad.flow_observation import FlowObservation


def bind_flow_observation_to_defense(
    defense: AdaptiveDefense,
    observation: FlowObservation,
    *,
    invariant_id: str,
    attack_class: str,
    source: str,
) -> DefenseRecord:
    """Create one unverified DefenseRecord from one immutable RCI-AD observation.

    The binding is intentionally one-way: observation becomes evidence, while
    AdaptiveDefense remains the authority for quarantine, verification, and
    promotion. The evidence includes a deterministic observation digest so the
    A/B boundary can carry provenance without carrying runtime state.
    """
    if not invariant_id or not attack_class or not source:
        raise ValueError("defense binding identity fields must be non-empty")

    payload: Mapping[str, object] = {
        "kind": "rci-ad-flow-observation",
        "timestamp": observation.timestamp,
        "baseline": observation.baseline,
        "observed": observation.observed,
        "decision": {
            "allowed": observation.decision.allowed,
            "throttle": observation.decision.throttle,
            "max_deviation": observation.decision.max_deviation,
            "limiting_dimension": observation.decision.limiting_dimension,
        },
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    observation_digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    evidence = json.dumps(
        {"observation_digest": observation_digest, "observation": payload},
        sort_keys=True,
        separators=(",", ":"),
    )
    return defense.observe_failure(
        invariant_id,
        attack_class,
        evidence,
        source=source,
    )


__all__ = ["bind_flow_observation_to_defense"]
