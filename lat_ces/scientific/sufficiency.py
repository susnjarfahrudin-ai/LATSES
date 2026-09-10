"""Minimal Scientific Sufficiency Contract.

This module is deliberately independent of HVAC solvers, security, GUI, and
RCI-AD. It answers only one epistemic question: are the supplied factors
sufficient for the stated engineering decision?
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class EvidenceState(str, Enum):
    DECLARED = "DECLARED"
    VERIFIED = "VERIFIED"
    MEASURED = "MEASURED"
    UNKNOWN = "UNKNOWN"


class SufficiencyStatus(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Factor:
    name: str
    evidence: EvidenceState
    value: Optional[float] = None
    uncertainty: Optional[float] = None
    sensitivity: Optional[float] = None

    @property
    def decision_effect(self) -> Optional[float]:
        """Maximum first-order decision displacement from this factor."""
        if self.uncertainty is None or self.sensitivity is None:
            return None
        return abs(self.uncertainty * self.sensitivity)


@dataclass(frozen=True)
class SufficiencyResult:
    status: SufficiencyStatus
    decision_margin: float
    limiting_factor: Optional[str] = None


def evaluate_sufficiency(
    factors: Tuple[Factor, ...], decision_margin: float
) -> SufficiencyResult:
    """Evaluate whether factor evidence and uncertainty support a decision.

    A relevant UNKNOWN factor is not sufficient merely because the current
    nominal result has a positive margin. If an unknown/uncertain factor has
    enough possible decision effect to consume that margin, the prior
    conclusion is explicitly revoked.
    """
    if decision_margin < 0:
        raise ValueError("decision_margin must be non-negative")

    for factor in factors:
        if factor.evidence is EvidenceState.UNKNOWN:
            effect = factor.decision_effect
            if effect is None:
                return SufficiencyResult(
                    SufficiencyStatus.UNKNOWN, decision_margin, factor.name
                )
            if effect >= decision_margin:
                return SufficiencyResult(
                    SufficiencyStatus.INSUFFICIENT, decision_margin, factor.name
                )

    return SufficiencyResult(SufficiencyStatus.SUFFICIENT, decision_margin)
