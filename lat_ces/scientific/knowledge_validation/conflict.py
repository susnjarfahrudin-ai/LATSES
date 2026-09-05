from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class KnowledgeConflict:
    claim_a: str
    claim_b: str
    evidence_a: str
    evidence_b: str
    status: str
    conflict_id: str | None = None

    def __post_init__(self) -> None:
        if self.conflict_id is None:
            object.__setattr__(self, "conflict_id", f"CONFLICT-{uuid4().hex[:12].upper()}")
