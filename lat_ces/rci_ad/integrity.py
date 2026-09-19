"""Independent integrity, trust, model self-test and revocation contracts."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import hashlib

class ModelSelfTestStatus(str,Enum): VALID="VALID"; INVALID="INVALID"
@dataclass(frozen=True)
class VerificationResult:
    integrity: bool
    self_test: ModelSelfTestStatus
    trusted: bool
    reason: str

def verify_artifact(content: bytes, trusted_hash: str) -> VerificationResult:
    actual=hashlib.sha256(content).hexdigest()
    ok=actual==trusted_hash
    return VerificationResult(ok,ModelSelfTestStatus.VALID,ok,"hash verified" if ok else "hash mismatch")

def verify_test_vectors(evaluator, vectors: tuple[tuple[object,object,float],...]) -> ModelSelfTestStatus:
    for value,expected,epsilon in vectors:
        actual=evaluator(value)
        if abs(actual-expected)>epsilon: return ModelSelfTestStatus.INVALID
    return ModelSelfTestStatus.VALID
