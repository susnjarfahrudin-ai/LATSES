"""Replaceable agent, task, boundary, invariant, and verification contracts."""

from dataclasses import dataclass, field
from typing import FrozenSet, Optional


@dataclass(frozen=True)
class AgentAuthority:
    """Capabilities granted to an agent; the agent cannot mutate its own set."""

    capabilities: FrozenSet[str] = field(default_factory=frozenset)

    def allows(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class SciTask:
    sci_id: str
    task_id: str
    owner: str
    capability: str
    boundary: str
    invariant: str
    verifier: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.sci_id, "sci_id"),
            (self.task_id, "task_id"),
            (self.owner, "owner"),
            (self.capability, "capability"),
            (self.boundary, "boundary"),
            (self.invariant, "invariant"),
            (self.verifier, "verifier"),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if self.owner == self.verifier:
            raise ValueError("owner and verifier must be independent")


def can_execute(task: SciTask, authority: AgentAuthority) -> bool:
    """Check authority without allowing the task owner to change authority."""
    return authority.allows(task.capability)


def revoke(authority: AgentAuthority, capability: str) -> AgentAuthority:
    """Return a reduced authority set; existing authority is never mutated."""
    return AgentAuthority(frozenset(c for c in authority.capabilities if c != capability))


def assign_replacement(task: SciTask, replacement: str) -> SciTask:
    """Replace a task owner while preserving its SCI contract and verifier."""
    if not replacement.strip():
        raise ValueError("replacement must not be empty")
    if replacement == task.verifier:
        raise ValueError("replacement and verifier must be independent")
    return SciTask(
        task.sci_id,
        task.task_id,
        replacement,
        task.capability,
        task.boundary,
        task.invariant,
        task.verifier,
    )
