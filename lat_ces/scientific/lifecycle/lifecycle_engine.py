from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

LIFECYCLE_STATES = ("CREATED", "DOCUMENTED", "VALIDATED", "ACTIVE", "UNDER_REVIEW", "ARCHIVED", "RETIRED")
_LIFECYCLE_TRANSITION_TOKEN = object()


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
    _transition_token: object | None = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        if not self.lifecycle_id:
            object.__setattr__(self, "lifecycle_id", f"LIFECYCLE-{uuid4().hex.upper()}")
        if self.state not in LIFECYCLE_STATES:
            raise ValueError("Invalid lifecycle state")
        if self.state != "CREATED" and self._transition_token is not _LIFECYCLE_TRANSITION_TOKEN:
            raise ValueError("Lifecycle state must be reached through LifecycleTransitionEngine")


class LifecycleTransitionEngine:
    ORDER = {state: index for index, state in enumerate(LIFECYCLE_STATES)}

    def transition(self, obj: ScientificKnowledgeLifecycleObject, target: str, timestamp: str) -> ScientificKnowledgeLifecycleObject:
        if target not in LIFECYCLE_STATES:
            raise ValueError("Unknown lifecycle state")
        if target == obj.state or self.ORDER[target] < self.ORDER[obj.state]:
            if not (obj.state == "UNDER_REVIEW" and target in {"VALIDATED", "ARCHIVED"}):
                raise ValueError(f"Invalid lifecycle transition: {obj.state} -> {target}")
        event = LifecycleEvent(target, timestamp, target)
        return ScientificKnowledgeLifecycleObject(
            obj.knowledge_id,
            target,
            obj.lifecycle_id,
            obj.history + (event,),
            _LIFECYCLE_TRANSITION_TOKEN,
        )


class ScientificKnowledgeLifecycleEngine:
    def create(self, knowledge_id: str) -> ScientificKnowledgeLifecycleObject:
        if not knowledge_id.strip():
            raise ValueError("Lifecycle requires knowledge identity")
        return ScientificKnowledgeLifecycleObject(knowledge_id)
