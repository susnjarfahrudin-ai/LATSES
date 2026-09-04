from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
import hashlib
import json

@dataclass(frozen=True)
class FederationEnvelope:
    envelope_id: str
    artifact_id: str
    issuer: str
    audience: str
    payload_hash: str

class GovernanceFederationEngine:
    def package(self, artifact_id: str, payload: object, *, issuer: str, audience: str) -> FederationEnvelope:
        if not artifact_id.strip() or not issuer.strip() or not audience.strip():
            raise ValueError("Federation requires artifact, issuer and audience")
        raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return FederationEnvelope(f"FED-{uuid4().hex.upper()}", artifact_id, issuer, audience, digest)

    def verify(self, envelope: FederationEnvelope, payload: object) -> bool:
        raw = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest() == envelope.payload_hash
