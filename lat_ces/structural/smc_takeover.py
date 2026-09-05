"""Neutral integration between ROM takeover signals and SMC-ROM selection.

The selector sees only candidate contract evidence. Candidate implementation
objects are intentionally absent from this boundary.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.structural.role_handover import TakeoverSignal
from lat_ces.structural.smc_selector import CandidateRecord, SelectorDecision, SMCROMSelector


@dataclass(frozen=True)
class SelectionCandidate:
    """Implementation-free candidate envelope for one operational role."""

    role_name: str
    evidence: CandidateRecord

    def __post_init__(self) -> None:
        if not self.role_name:
            raise ValueError("role_name must not be empty")


def select_takeover_candidate(
    selector: SMCROMSelector,
    signal: TakeoverSignal,
    candidates: tuple[SelectionCandidate, ...],
) -> SelectorDecision:
    """Select the first eligible candidate for the takeover recipient role.

    Candidate ordering is supplied by SMC-ROM operational policy. The selector
    receives only the candidate's neutral evidence and never its implementation.
    """
    matching = [item.evidence for item in candidates if item.role_name == signal.recipient_role.value]
    if not matching:
        raise ValueError("no candidate available for takeover role")
    for evidence in matching:
        if evidence.eligible:
            return selector.select(evidence)
    raise ValueError("no eligible candidate available for takeover role")


__all__ = ["SelectionCandidate", "select_takeover_candidate"]
