from enum import Enum


class KnowledgeState(str, Enum):
    UNKNOWN = "UNKNOWN"
    HYPOTHESIS = "HYPOTHESIS"
    SUPPORTED = "SUPPORTED"
    VALIDATED = "VALIDATED"
    CONFIRMED = "CONFIRMED"


class InvalidKnowledgeTransition(ValueError):
    pass


class KnowledgeStateMachine:
    ALLOWED = {
        KnowledgeState.UNKNOWN: (KnowledgeState.HYPOTHESIS,),
        KnowledgeState.HYPOTHESIS: (KnowledgeState.SUPPORTED,),
        KnowledgeState.SUPPORTED: (KnowledgeState.VALIDATED,),
        KnowledgeState.VALIDATED: (KnowledgeState.CONFIRMED,),
        KnowledgeState.CONFIRMED: (),
    }

    def __init__(self, initial: KnowledgeState = KnowledgeState.UNKNOWN):
        self._state = initial
        self._history = [initial]

    @property
    def state(self) -> KnowledgeState:
        return self._state

    @property
    def history(self) -> tuple[KnowledgeState, ...]:
        return tuple(self._history)

    def transition(self, target: KnowledgeState) -> KnowledgeState:
        if target not in self.ALLOWED[self._state]:
            raise InvalidKnowledgeTransition(f"Illegal knowledge state transition: {self._state.value} -> {target.value}")
        self._state = target
        self._history.append(target)
        return target
