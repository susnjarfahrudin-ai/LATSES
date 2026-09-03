from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class AdaptiveSecurityState:
    mode: str
    controls: tuple[str, ...]
    rollback_reference: str
    human_oversight_required: bool = True

class AdaptiveSecurityGovernance:
    def evaluate(self, integrity: bool, risk: str, rollback_available: bool) -> AdaptiveSecurityState:
        if not rollback_available:
            return AdaptiveSecurityState("SAFE_MODE", ("BLOCK_CHANGES",), "NONE", True)
        if not integrity or risk.upper() in {"HIGH", "CRITICAL"}:
            return AdaptiveSecurityState("HUMAN_REVIEW_REQUIRED", ("ISOLATE", "AUDIT", "ROLLBACK_READY"), "LAST_KNOWN_GOOD", True)
        return AdaptiveSecurityState("NORMAL", ("AUDIT", "MONITOR"), "LAST_KNOWN_GOOD", True)
