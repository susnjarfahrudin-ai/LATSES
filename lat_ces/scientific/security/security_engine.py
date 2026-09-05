from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from uuid import uuid4

@dataclass(frozen=True)
class SecurityEnvelope:
    envelope_id: str
    subject_id: str
    issuer: str
    payload_hash: str

class FederationSecurityEngine:
    def seal(self, subject_id: str, payload: object, issuer: str) -> SecurityEnvelope:
        if not subject_id.strip() or not issuer.strip():
            raise ValueError("Security envelope requires subject and issuer")
        raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
        return SecurityEnvelope(f"SEC-{uuid4().hex.upper()}", subject_id, issuer, hashlib.sha256(raw.encode("utf-8")).hexdigest())
    def verify(self, envelope: SecurityEnvelope, payload: object) -> bool:
        raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest() == envelope.payload_hash
