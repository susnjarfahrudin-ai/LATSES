from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4

LIFECYCLE_STATES = ("CREATED", "DOCUMENTED", "VALIDATED", "ACTIVE", "UNDER_REVIEW", "ARCHIVED", "RETIRED")

@dataclass(frozen=True)
class LifecycleEvent:
    event: str
    timestamp: str
    state: str

@dataclass(frozen=True)
class ScientificKnowledgeLifecycleObject:
    knowledge_id: str
    state: str = "CREATED"
    lifecycle_id: str = ""
    history: tuple[LifecycleEvent, ...] = ()

    def __post_init__(self) -> None:
        if not self.lifecycle_id:
            object.__setattr__(self, "lifecycle_id", f"LIFECYCLE-{uuid4().hex.upper()}")
        if self.state not in LIFECYCLE_STATES:
            raise ValueError("Invalid lifecycle state")

class LifecycleTransitionEngine:
    ORDER = {state: index for index, state in enumerate(LIFECYCLE_STATES)}
    def transition(self, obj: ScientificKnowledgeLifecycleObject, target: str, timestamp: str) -> ScientificKnowledgeLifecycleObject:
        if target not in LIFECYCLE_STATES:
            raise ValueError("Unknown lifecycle state")
        if target == obj.state or self.ORDER[target] < self.ORDER[obj.state]:
            if not (obj.state == "UNDER_REVIEW" and target in {"VALIDATED", "ARCHIVED"}):
                raise ValueError(f"Invalid lifecycle transition: {obj.state} -> {target}")
        event = LifecycleEvent(target, timestamp, target)
        return ScientificKnowledgeLifecycleObject(obj.knowledge_id, target, obj.lifecycle_id, obj.history + (event,))

class ScientificKnowledgeLifecycleEngine:
    def create(self, knowledge_id: str) -> ScientificKnowledgeLifecycleObject:
        if not knowledge_id.strip():
            raise ValueError("Lifecycle requires knowledge identity")
        return ScientificKnowledgeLifecycleObject(knowledge_id)
