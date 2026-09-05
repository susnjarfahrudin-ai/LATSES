"""Neutral restart reconstruction contract for SMC-ROM operational state.

Reconstruction consumes preserved evidence and produces a bounded immutable
state snapshot. It does not activate candidates, execute models, or rewrite
historical decision records.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconstructionEvidence:
    """Evidence permitted as input to restart reconstruction."""

    decision_ids: tuple[str, ...]
    registry_version: str
    applicability_passed: bool
    contract_passed: bool
    selector_version: str

    def __post_init__(self) -> None:
        if not self.registry_version:
            raise ValueError("registry_version must not be empty")
        if not self.selector_version:
            raise ValueError("selector_version must not be empty")
        if len(set(self.decision_ids)) != len(self.decision_ids):
            raise ValueError("decision_ids must be unique")


@dataclass(frozen=True)
class ReconstructedOperationalState:
    """Bounded state reconstructed from preserved evidence, never auto-active."""

    decision_ids: tuple[str, ...]
    registry_version: str
    selector_version: str
    state: str


class RestartReconstructor:
    """Reconstruct permitted operational state without activation or mutation."""

    def reconstruct(self, evidence: ReconstructionEvidence) -> ReconstructedOperationalState:
        if not evidence.applicability_passed or not evidence.contract_passed:
            return ReconstructedOperationalState(
                decision_ids=evidence.decision_ids,
                registry_version=evidence.registry_version,
                selector_version=evidence.selector_version,
                state="BLOCKED",
            )
        return ReconstructedOperationalState(
            decision_ids=evidence.decision_ids,
            registry_version=evidence.registry_version,
            selector_version=evidence.selector_version,
            state="RECONSTRUCTED",
        )


__all__ = [
    "ReconstructionEvidence",
    "ReconstructedOperationalState",
    "RestartReconstructor",
]
