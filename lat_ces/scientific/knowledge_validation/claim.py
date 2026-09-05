from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from .validation_state import KnowledgeState


@dataclass(frozen=True)
class ScientificClaim:
    statement: str
    domain: str
    claim_id: str | None = None
    created: str | None = None
    status: KnowledgeState = KnowledgeState.UNKNOWN

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("Claim statement is required")
        if not self.domain.strip():
            raise ValueError("Claim domain is required")
        if self.claim_id is None:
            object.__setattr__(self, "claim_id", f"CLAIM-{uuid4().hex[:12].upper()}")
        if self.created is None:
            object.__setattr__(self, "created", datetime.now(timezone.utc).isoformat())
