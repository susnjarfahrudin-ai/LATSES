"""Adaptive defense knowledge for failover and recovery."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import threading

@dataclass(frozen=True)
class DefenseRecord:
    invariant_id: str
    attack_class: str
    evidence: str
    source: str
    verification_sha: str | None = None
    verified: bool = False
    def __post_init__(self) -> None:
        if not self.invariant_id or not self.attack_class or not self.evidence or not self.source:
            raise ValueError("defense record identity fields must be non-empty")
        if self.verified and not self.verification_sha:
            raise ValueError("verified defense records require verification_sha")
    @property
    def digest(self) -> str:
        payload = {"invariant_id": self.invariant_id, "attack_class": self.attack_class, "evidence": self.evidence, "source": self.source, "verification_sha": self.verification_sha, "verified": self.verified}
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

class AdaptiveDefense:
    def __init__(self) -> None:
        self._records: dict[str, DefenseRecord] = {}
        self._quarantined: set[str] = set()
        self._lock = threading.Lock()
    def observe_failure(self, invariant_id: str, attack_class: str, evidence: str, *, source: str = "A") -> DefenseRecord:
        record = DefenseRecord(invariant_id, attack_class, evidence, source)
        with self._lock: self._records[invariant_id] = record
        return record
    def quarantine(self, record: DefenseRecord) -> None:
        with self._lock:
            self._records.setdefault(record.invariant_id, record)
            self._quarantined.add(record.invariant_id)
    def is_quarantined(self, invariant_id: str) -> bool:
        with self._lock: return invariant_id in self._quarantined
    def promote(self, record: DefenseRecord, *, verification_sha: str) -> DefenseRecord:
        if not verification_sha: raise ValueError("verification_sha must be non-empty")
        verified = DefenseRecord(record.invariant_id, record.attack_class, record.evidence, record.source, verification_sha, True)
        with self._lock:
            self._records[verified.invariant_id] = verified
            self._quarantined.add(verified.invariant_id)
        return verified
    def import_verified(self, record: DefenseRecord) -> None:
        if not record.verified or not record.verification_sha:
            raise ValueError("only verified defense records may be imported")
        with self._lock:
            self._records[record.invariant_id] = record
            self._quarantined.add(record.invariant_id)
    def records(self) -> tuple[DefenseRecord, ...]:
        with self._lock: return tuple(self._records[key] for key in sorted(self._records))
    def export_verified(self) -> tuple[DefenseRecord, ...]:
        return tuple(record for record in self.records() if record.verified)

__all__ = ["AdaptiveDefense", "DefenseRecord"]
