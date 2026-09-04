"""Read-only security defense history and verified lesson reader.

The history is an independent evidence/literature layer. Runtime security
components never write to it. Only records carrying explicit Verification
identity are exposed as learnable lessons to A/B.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

REQUIRED_FIELDS = {"record_id", "status", "attack_class", "invariant", "dimensions", "baseline", "observation", "response", "verification_sha"}
VALID_STATUSES = {"observed", "contained", "verified", "learned"}
DIMENSIONS = ("frequency", "volume", "concurrency", "novelty")

@dataclass(frozen=True)
class DefenseHistoryRecord:
    """Immutable historical defense evidence."""
    record_id: str
    status: str
    attack_class: str
    invariant: str
    dimensions: tuple[str, ...]
    baseline: Mapping[str, float]
    observation: Mapping[str, Any]
    response: Mapping[str, Any]
    verification_sha: str | None

    @property
    def verified(self) -> bool:
        return self.status in {"verified", "learned"} and bool(self.verification_sha)

    def as_dict(self) -> dict[str, Any]:
        return {"record_id": self.record_id, "status": self.status, "attack_class": self.attack_class, "invariant": self.invariant, "dimensions": list(self.dimensions), "baseline": dict(self.baseline), "observation": dict(self.observation), "response": dict(self.response), "verification_sha": self.verification_sha}

class DefenseHistory:
    """Read-only access to the independent defense-history ledger.

    There is deliberately no append/update/delete API. A/B learning can only
    consume records that carry an explicit Verification SHA.
    """
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._records = self._load()

    def _load(self) -> tuple[DefenseHistoryRecord, ...]:
        if not self._path.is_file():
            raise FileNotFoundError(self._path)
        records: list[DefenseHistoryRecord] = []
        for line_number, line in enumerate(self._path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid defense-history JSON at line {line_number}") from exc
            records.append(self._validate(raw, line_number))
        return tuple(records)

    @staticmethod
    def _validate(raw: Any, line_number: int) -> DefenseHistoryRecord:
        if not isinstance(raw, dict) or set(raw) != REQUIRED_FIELDS:
            raise ValueError(f"invalid defense-history schema at line {line_number}")
        if not all(isinstance(raw[field], str) and raw[field] for field in ("record_id", "status", "attack_class", "invariant")):
            raise ValueError(f"invalid defense-history identity at line {line_number}")
        if raw["status"] not in VALID_STATUSES:
            raise ValueError(f"invalid defense-history status at line {line_number}")
        dimensions = raw["dimensions"]
        if not isinstance(dimensions, list) or not dimensions or not all(item in DIMENSIONS for item in dimensions):
            raise ValueError(f"invalid defense-history dimensions at line {line_number}")
        baseline = raw["baseline"]
        if not isinstance(baseline, dict) or set(baseline) != set(DIMENSIONS):
            raise ValueError(f"invalid defense-history baseline at line {line_number}")
        try:
            baseline_float = {name: float(baseline[name]) for name in DIMENSIONS}
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid defense-history baseline values at line {line_number}") from exc
        if any(not math.isfinite(value) or value <= 0.0 for value in baseline_float.values()):
            raise ValueError(f"invalid defense-history baseline values at line {line_number}")
        if not isinstance(raw["observation"], dict) or not isinstance(raw["response"], dict):
            raise ValueError(f"invalid defense-history evidence at line {line_number}")
        sha = raw["verification_sha"]
        if sha is not None and (not isinstance(sha, str) or not sha):
            raise ValueError(f"invalid defense-history verification_sha at line {line_number}")
        if raw["status"] in {"verified", "learned"} and not sha:
            raise ValueError(f"verified defense-history record requires verification_sha at line {line_number}")
        return DefenseHistoryRecord(raw["record_id"], raw["status"], raw["attack_class"], raw["invariant"], tuple(dimensions), MappingProxyType(baseline_float), MappingProxyType(dict(raw["observation"])), MappingProxyType(dict(raw["response"])), sha)

    def records(self) -> tuple[DefenseHistoryRecord, ...]:
        return self._records

    def verified_lessons(self) -> tuple[DefenseHistoryRecord, ...]:
        """Return only evidence that A/B is permitted to learn from."""
        return tuple(record for record in self._records if record.verified)

__all__ = ["DefenseHistory", "DefenseHistoryRecord"]
