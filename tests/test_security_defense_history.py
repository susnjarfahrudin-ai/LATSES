from __future__ import annotations

import json

import pytest

from lat_ces.security.defense_history import DefenseHistory
from lat_ces.security.flow_guard import FlowGuard


BASELINE = {
    "frequency": 100.0,
    "volume": 100.0,
    "concurrency": 100.0,
    "novelty": 100.0,
}


def test_defense_history_exposes_only_verified_lessons(tmp_path):
    path = tmp_path / "history.jsonl"
    records = [
        {
            "record_id": "contained-1",
            "status": "contained",
            "attack_class": "probe",
            "invariant": "fixed baseline",
            "dimensions": ["frequency", "volume", "concurrency", "novelty"],
            "baseline": BASELINE,
            "observation": {"deviation": 0.19},
            "response": {"action": "throttle"},
            "verification_sha": None,
        },
        {
            "record_id": "learned-1",
            "status": "learned",
            "attack_class": "flow-edge",
            "invariant": "20% admission stop",
            "dimensions": ["frequency"],
            "baseline": BASELINE,
            "observation": {"deviation": 0.20, "duration_seconds": 1.0},
            "response": {"action": "admission-stop"},
            "verification_sha": "verification-sha-002",
        },
    ]
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")

    history = DefenseHistory(path)
    assert [item.record_id for item in history.verified_lessons()] == ["learned-1"]
    with pytest.raises(TypeError):
        history.records()[0].baseline["frequency"] = 200
    assert not hasattr(history, "append")
    assert not hasattr(history, "write")


def test_defense_history_rejects_learned_without_verification_sha(tmp_path):
    path = tmp_path / "history.jsonl"
    record = {
        "record_id": "bad-1",
        "status": "learned",
        "attack_class": "probe",
        "invariant": "fixed baseline",
        "dimensions": ["frequency"],
        "baseline": BASELINE,
        "observation": {},
        "response": {},
        "verification_sha": None,
    }
    path.write_text(json.dumps(record) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="verification_sha"):
        DefenseHistory(path)


def test_flow_guard_rejects_type_coercion_in_untrusted_dimensions():
    guard = FlowGuard(BASELINE)
    for value in (True, False, "100", "1e2"):
        with pytest.raises(ValueError):
            guard.evaluate({
                "frequency": value,
                "volume": 100.0,
                "concurrency": 100.0,
                "novelty": 100.0,
            })
