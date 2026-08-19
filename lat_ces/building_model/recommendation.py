"""AI recommendation contract: advisory, evidence-linked, human-controlled."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List


class RecommendationState(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EDITED = "EDITED"


@dataclass(frozen=True)
class Evidence:
    source: str
    kind: str  # STANDARD / DATASHEET / MEASURED / RESEARCH / USER_EXPERIENCE
    confidence: str = "UNKNOWN"
    note: str = ""


@dataclass
class Recommendation:
    id: str
    title: str
    reason: str
    expected_benefit: str
    risks: str = ""
    evidence: List[Evidence] = field(default_factory=list)
    state: RecommendationState = RecommendationState.PROPOSED

    def accept(self) -> None:
        self.state = RecommendationState.ACCEPTED

    def reject(self) -> None:
        self.state = RecommendationState.REJECTED

    def edit(self) -> None:
        self.state = RecommendationState.EDITED
