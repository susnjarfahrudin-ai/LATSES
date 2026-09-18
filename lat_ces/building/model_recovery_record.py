"""Authoritative persistence boundary for BuildingModel recovery records.

This module deliberately does not select a recovery candidate or reconstruct a
BuildingModel. It wraps the existing ``project_io`` payload with identity,
lineage, lifecycle metadata, and an integrity digest.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


SCHEMA = "LAT-CES-MODEL-RECOVERY-1"


def _canonical_json(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _integrity_material(
    *,
    record_id: str,
    model_id: str,
    revision: int,
    parent_revision: int | None,
    created_at: str,
    lifecycle_status: str,
    selector_role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "model_id": model_id,
        "revision": revision,
        "parent_revision": parent_revision,
        "created_at": created_at,
        "lifecycle_status": lifecycle_status,
        "selector_role": selector_role,
        "payload": payload,
    }


def _digest(value: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


@dataclass(frozen=True)
class ModelRecoveryRecord:
    """Immutable wrapper around an existing ``project_io`` payload."""

    record_id: str
    model_id: str
    revision: int
    parent_revision: int | None
    created_at: str
    integrity: str
    lifecycle_status: str
    selector_role: str
    payload: dict[str, Any]

    @classmethod
    def create(
        cls,
        *,
        record_id: str,
        model_id: str,
        revision: int,
        payload: dict[str, Any],
        parent_revision: int | None = None,
        lifecycle_status: str = "VALID",
        selector_role: str = "NONE",
    ) -> "ModelRecoveryRecord":
        if revision < 0:
            raise ValueError("revision must be non-negative")
        if parent_revision is not None and parent_revision >= revision:
            raise ValueError("parent_revision must be lower than revision")
        if not model_id:
            raise ValueError("model_id is required")
        created_at = datetime.now(timezone.utc).isoformat()
        return cls(
            record_id=record_id,
            model_id=model_id,
            revision=revision,
            parent_revision=parent_revision,
            created_at=created_at,
            integrity=_digest(
                _integrity_material(
                    record_id=record_id,
                    model_id=model_id,
                    revision=revision,
                    parent_revision=parent_revision,
                    created_at=created_at,
                    lifecycle_status=lifecycle_status,
                    selector_role=selector_role,
                    payload=payload,
                )
            ),
            lifecycle_status=lifecycle_status,
            selector_role=selector_role,
            payload=payload,
        )

    def verify_integrity(self) -> bool:
        return _digest(
            _integrity_material(
                record_id=self.record_id,
                model_id=self.model_id,
                revision=self.revision,
                parent_revision=self.parent_revision,
                created_at=self.created_at,
                lifecycle_status=self.lifecycle_status,
                selector_role=self.selector_role,
                payload=self.payload,
            )
        ) == self.integrity

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA,
            "record_id": self.record_id,
            "model_id": self.model_id,
            "revision": self.revision,
            "parent_revision": self.parent_revision,
            "created_at": self.created_at,
            "integrity": self.integrity,
            "lifecycle_status": self.lifecycle_status,
            "selector_role": self.selector_role,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelRecoveryRecord":
        if data.get("schema") != SCHEMA:
            raise ValueError("unsupported Model Recovery Record schema")
        record = cls(
            record_id=str(data["record_id"]),
            model_id=str(data["model_id"]),
            revision=int(data["revision"]),
            parent_revision=(None if data.get("parent_revision") is None else int(data["parent_revision"])),
            created_at=str(data["created_at"]),
            integrity=str(data["integrity"]),
            lifecycle_status=str(data["lifecycle_status"]),
            selector_role=str(data["selector_role"]),
            payload=dict(data["payload"]),
        )
        if not record.verify_integrity():
            raise ValueError("Model Recovery Record integrity check failed")
        return record


__all__ = ["ModelRecoveryRecord", "SCHEMA"]
