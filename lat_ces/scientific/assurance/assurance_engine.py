from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

@dataclass(frozen=True)
class AssuranceCriteria:
    validation: bool
    integrity: bool
    trust_score: float
    governance: bool
    preservation: bool

@dataclass(frozen=True)
class AssuranceLevel:
    name: str

@dataclass(frozen=True)
class AssuranceAssessment:
    knowledge_id: str
    level: str
    criteria: AssuranceCriteria
    reason: str
    assessment_id: str = ""

class ScientificKnowledgeAssuranceEngine:
    def assess(self, knowledge_id: str, criteria: AssuranceCriteria) -> AssuranceAssessment:
        if not knowledge_id.strip():
            raise ValueError("Assurance requires knowledge identity")
        if not 0.0 <= criteria.trust_score <= 1.0:
            raise ValueError("Trust score must be within [0, 1]")
        if criteria.validation and criteria.integrity and criteria.governance and criteria.preservation and criteria.trust_score >= 0.75:
            level, reason = "ASSURED", "All assurance criteria satisfied"
        elif criteria.validation and criteria.integrity:
            level, reason = "CONDITIONAL", "Core evidence conditions satisfied; review remains required"
        else:
            level, reason = "REVIEW_REQUIRED", "Required validation or integrity evidence missing"
        return AssuranceAssessment(knowledge_id, level, criteria, reason, f"ASSURANCE-{uuid4().hex.upper()}")
