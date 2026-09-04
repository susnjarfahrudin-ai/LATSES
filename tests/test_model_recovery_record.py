from __future__ import annotations

import json

import pytest

from lat_ces.building.model_recovery_record import ModelRecoveryRecord, SCHEMA


def test_model_recovery_record_create_serialize_read_verify(tmp_path):
    payload = {
        "schema": "LAT-CES-BUILDING-8",
        "model": {"name": "Reference House", "model_id": "BLDG-001", "levels": []},
        "current_step": 1,
    }

    record = ModelRecoveryRecord.create(
        record_id="REC-001",
        model_id="BLDG-001",
        revision=3,
        parent_revision=2,
        payload=payload,
        selector_role="NONE",
    )

    path = tmp_path / "recovery-record.json"
    path.write_text(json.dumps(record.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    loaded = ModelRecoveryRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    assert loaded.record_id == record.record_id
    assert loaded.model_id == record.model_id
    assert loaded.revision == 3
    assert loaded.parent_revision == 2
    assert loaded.payload == payload
    assert loaded.integrity == record.integrity
    assert loaded.verify_integrity()
    assert loaded.to_dict()["schema"] == SCHEMA


def test_model_recovery_record_rejects_tampered_payload():
    record = ModelRecoveryRecord.create(
        record_id="REC-002",
        model_id="BLDG-002",
        revision=1,
        payload={"model": {"model_id": "BLDG-002"}},
    )
    data = record.to_dict()
    data["payload"]["model"]["model_id"] = "BLDG-TAMPERED"

    with pytest.raises(ValueError, match="integrity"):
        ModelRecoveryRecord.from_dict(data)


def test_model_recovery_record_rejects_tampered_authoritative_metadata():
    record = ModelRecoveryRecord.create(
        record_id="REC-ATTACK",
        model_id="BLDG-ATTACK",
        revision=4,
        parent_revision=3,
        payload={"model": {"model_id": "BLDG-ATTACK"}},
    )
    data = record.to_dict()
    data["model_id"] = "BLDG-IMPOSTOR"
    data["revision"] = 99
    data["selector_role"] = "LKG"

    with pytest.raises(ValueError, match="integrity"):
        ModelRecoveryRecord.from_dict(data)


def test_model_recovery_record_rejects_invalid_lineage():
    with pytest.raises(ValueError, match="parent_revision"):
        ModelRecoveryRecord.create(
            record_id="REC-003",
            model_id="BLDG-003",
            revision=2,
            parent_revision=2,
            payload={},
        )
