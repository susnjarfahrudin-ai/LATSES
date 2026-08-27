from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class AuditRecord:
    action: str
    actor: str
    object_id: str
    reason: str
    result: str = "RECORDED"
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc).isoformat())
        if not all(value.strip() for value in (self.action, self.actor, self.object_id, self.reason, self.result)):
            raise ValueError("AuditRecord requires action, actor, object, reason and result")
