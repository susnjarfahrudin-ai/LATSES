"""Model-free SMC-ROM selector contract.

SMC-ROM manages lifecycle decisions from immutable candidate evidence. It does
not inspect, mutate, or identify another model's implementation.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum


BENCH_CAPACITY = 10


class CandidateState(str, Enum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    BENCHED = "BENCHED"
    RETIRED = "RETIRED"
    INVALID = "INVALID"
    SUPERSEDED = "SUPERSEDED"


@dataclass(frozen=True)
class CandidateRecord:
    """Immutable operational evidence for one selectable model instance."""

    candidate_id: str
    version: str
    applicability_passed: bool
    contract_passed: bool
    provenance: str

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id must not be empty")
        if not self.version:
            raise ValueError("version must not be empty")
        if not self.provenance:
            raise ValueError("provenance must not be empty")

    @property
    def eligible(self) -> bool:
        return self.applicability_passed and self.contract_passed


@dataclass(frozen=True)
class SelectorDecision:
    """Immutable lifecycle decision with provenance and optional supersession."""

    operation: str
    candidate_id: str
    resulting_state: CandidateState
    provenance: str
    supersedes_candidate_id: str | None = None


@dataclass(frozen=True)
class ReconstructionResult:
    """Immutable operational-state reconstruction evidence after restart."""

    candidate_ids: tuple[str, ...]
    active_candidate_id: str | None
    provenance: str


class SMCROMSelector:
    """Bounded, deterministic selector operating only on neutral candidate evidence."""

    def __init__(self, bench_capacity: int = BENCH_CAPACITY) -> None:
        if bench_capacity <= 0:
            raise ValueError("bench_capacity must be positive")
        self._bench_capacity = bench_capacity
        self._bench: deque[str] = deque()
        self._active_candidate_id: str | None = None
        self._states: dict[str, CandidateState] = {}
        self._history: list[SelectorDecision] = []

    @property
    def bench_ids(self) -> tuple[str, ...]:
        return tuple(self._bench)

    @property
    def active_candidate_id(self) -> str | None:
        return self._active_candidate_id

    @property
    def history(self) -> tuple[SelectorDecision, ...]:
        return tuple(self._history)

    def select(self, candidate: CandidateRecord) -> SelectorDecision:
        """Select an eligible candidate explicitly; no scientific-truth claim is made."""
        if not candidate.eligible:
            return self.reject(candidate, reason="eligibility-failed")
        previous = self._active_candidate_id
        if previous is not None and previous != candidate.candidate_id:
            self._states[previous] = CandidateState.SUPERSEDED
        if candidate.candidate_id in self._bench:
            self._bench.remove(candidate.candidate_id)
        self._states[candidate.candidate_id] = CandidateState.ACTIVE
        self._active_candidate_id = candidate.candidate_id
        decision = SelectorDecision(
            "select", candidate.candidate_id, CandidateState.ACTIVE,
            candidate.provenance, supersedes_candidate_id=previous,
        )
        self._history.append(decision)
        return decision

    def reject(self, candidate: CandidateRecord, reason: str) -> SelectorDecision:
        """Reject a candidate without deleting its historical decision record."""
        decision = SelectorDecision(
            "reject", candidate.candidate_id, CandidateState.INVALID,
            f"{candidate.provenance}:{reason}",
        )
        self._states[candidate.candidate_id] = CandidateState.INVALID
        self._history.append(decision)
        return decision

    def bench(self, candidate: CandidateRecord) -> SelectorDecision:
        """Place an eligible candidate on a bounded FIFO operational bench."""
        if not candidate.eligible:
            return self.reject(candidate, reason="eligibility-failed")
        if candidate.candidate_id == self._active_candidate_id:
            raise ValueError("active candidate cannot be placed on the bench")
        if candidate.candidate_id in self._bench:
            self._bench.remove(candidate.candidate_id)
        self._bench.append(candidate.candidate_id)
        self._states[candidate.candidate_id] = CandidateState.BENCHED
        while len(self._bench) > self._bench_capacity:
            evicted = self._bench.popleft()
            self._states[evicted] = CandidateState.RETIRED
        decision = SelectorDecision("bench", candidate.candidate_id, CandidateState.BENCHED, candidate.provenance)
        self._history.append(decision)
        return decision

    def replace(self, candidate: CandidateRecord) -> SelectorDecision:
        """Replace the active candidate only with a currently eligible candidate."""
        if not candidate.eligible:
            return self.reject(candidate, reason="replacement-ineligible")
        previous = self._active_candidate_id
        if previous is not None and previous != candidate.candidate_id:
            self._states[previous] = CandidateState.SUPERSEDED
        self._active_candidate_id = candidate.candidate_id
        self._states[candidate.candidate_id] = CandidateState.ACTIVE
        if candidate.candidate_id in self._bench:
            self._bench.remove(candidate.candidate_id)
        decision = SelectorDecision(
            "replace", candidate.candidate_id, CandidateState.ACTIVE,
            candidate.provenance, supersedes_candidate_id=previous,
        )
        self._history.append(decision)
        return decision

    def recover(self, candidate_id: str, checkpoint_provenance: str) -> SelectorDecision:
        """Recover an inactive candidate from preserved evidence without activating it."""
        if self._states.get(candidate_id) not in {
            CandidateState.INVALID,
            CandidateState.RETIRED,
            CandidateState.SUPERSEDED,
        }:
            raise ValueError("recovery requires an inactive candidate")
        if candidate_id in self._bench:
            self._bench.remove(candidate_id)
        self._bench.append(candidate_id)
        self._states[candidate_id] = CandidateState.BENCHED
        while len(self._bench) > self._bench_capacity:
            evicted = self._bench.popleft()
            self._states[evicted] = CandidateState.RETIRED
        decision = SelectorDecision("recover", candidate_id, CandidateState.BENCHED, checkpoint_provenance)
        self._history.append(decision)
        return decision

    def reconstruct(
        self,
        bench_candidate_ids: tuple[str, ...],
        active_candidate_id: str | None,
        provenance: str,
    ) -> ReconstructionResult:
        """Reconstruct bounded operational state from neutral preserved identifiers."""
        if len(bench_candidate_ids) > self._bench_capacity:
            raise ValueError("reconstructed bench exceeds capacity")
        if active_candidate_id is not None and active_candidate_id in bench_candidate_ids:
            raise ValueError("active candidate cannot be part of reconstructed bench")
        self._bench.clear()
        self._bench.extend(bench_candidate_ids)
        self._active_candidate_id = active_candidate_id
        if active_candidate_id is not None:
            self._states[active_candidate_id] = CandidateState.ACTIVE
        for candidate_id in bench_candidate_ids:
            self._states[candidate_id] = CandidateState.BENCHED
        return ReconstructionResult(bench_candidate_ids, active_candidate_id, provenance)


__all__ = [
    "BENCH_CAPACITY",
    "CandidateState",
    "CandidateRecord",
    "SelectorDecision",
    "ReconstructionResult",
    "SMCROMSelector",
]
