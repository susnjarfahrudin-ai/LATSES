from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4
import hashlib
import json

@dataclass(frozen=True)
class ScientificMetadata:
    knowledge_id: str
    version: str
    source: str
    created_at: str

@dataclass(frozen=True)
class ScientificKnowledgePreservationObject:
    knowledge_id: str
    data: object
    metadata: ScientificMetadata
    state: str = "AVAILABLE"
    preservation_id: str = ""

    def __post_init__(self) -> None:
        if not self.preservation_id:
            object.__setattr__(self, "preservation_id", f"PRESERVATION-{uuid4().hex.upper()}")
        if self.state not in {"AVAILABLE", "ARCHIVED", "RECOVERED"}:
            raise ValueError("Invalid preservation state")

class IntegrityManager:
    @staticmethod
    def hash(data: object) -> str:
        raw = json.dumps(data, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def verify(cls, data: object, expected_hash: str) -> bool:
        return cls.hash(data) == expected_hash

class ScientificArchive:
    def __init__(self) -> None:
        self.records: dict[str, ScientificKnowledgePreservationObject] = {}
    def store(self, record: ScientificKnowledgePreservationObject) -> None:
        self.records[record.preservation_id] = record
    def get(self, preservation_id: str):
        return self.records.get(preservation_id)

class VersionStore:
    def __init__(self) -> None:
        self.versions: dict[str, list[object]] = {}
    def add(self, knowledge_id: str, version: object) -> None:
        self.versions.setdefault(knowledge_id, []).append(version)
    def history(self, knowledge_id: str) -> tuple[object, ...]:
        return tuple(self.versions.get(knowledge_id, ()))

class PreservationMigration:
    def migrate(self, old_format: str, new_format: str) -> dict[str, str]:
        if not old_format.strip() or not new_format.strip():
            raise ValueError("Migration requires source and target formats")
        return {"from": old_format, "to": new_format, "status": "MIGRATED"}

class RecoveryManager:
    def recover(self, backup: object) -> dict[str, object]:
        if backup is None:
            raise ValueError("Recovery requires a backup")
        return {"state": "RECOVERED", "source": backup}

class ScientificKnowledgePreservationEngine:
    def __init__(self) -> None:
        self.archive = ScientificArchive()
        self.versions = VersionStore()
    def preserve(self, knowledge_id: str, data: object, *, version: str = "1", source: str = "UNKNOWN") -> ScientificKnowledgePreservationObject:
        metadata = ScientificMetadata(knowledge_id, version, source, datetime.now(timezone.utc).isoformat())
        record = ScientificKnowledgePreservationObject(knowledge_id, data, metadata)
        self.archive.store(record)
        self.versions.add(knowledge_id, record)
        return record
