from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class SecurityGovernanceDecision:
    decision_id: str
    subject: str
    authority: str
    risk: str
    status: str

class SecurityHardeningGovernanceEngine:
    def evaluate(self, subject: str, authority: str, risk: str) -> SecurityGovernanceDecision:
        if not subject.strip() or not authority.strip() or not risk.strip():
            raise ValueError("Security governance requires subject, authority and risk")
        status = "GOVERNANCE_REVIEW" if risk.upper() in {"HIGH", "CRITICAL"} else "UNDER_REVIEW"
        return SecurityGovernanceDecision(f"SGOV-{uuid4().hex.upper()}", subject, authority, risk, status)
