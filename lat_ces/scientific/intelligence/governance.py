from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class IntelligenceGovernanceDecision:
    decision_id: str
    action: str
    authority: str
    evidence: tuple[str, ...]
    status: str

class IntelligenceGovernanceEngine:
    def evaluate(self, action: str, authority: str, evidence: tuple[str, ...]) -> IntelligenceGovernanceDecision:
        if not action.strip() or not authority.strip():
            raise ValueError("Intelligence governance requires action and authority")
        if not evidence:
            raise ValueError("Intelligence governance requires evidence")
        return IntelligenceGovernanceDecision(f"IGOV-{uuid4().hex.upper()}", action, authority, tuple(evidence), "UNDER_REVIEW")
