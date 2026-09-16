"""Neutral evidence-state vocabulary for catalog/presentation surfaces."""
from __future__ import annotations

from enum import StrEnum


class EvidenceState(StrEnum):
    DECLARED = "DECLARED"
    ACCEPTED_FOR_CALCULATION = "ACCEPTED_FOR_CALCULATION"
    VERIFIED = "VERIFIED"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    REJECTED = "REJECTED"


def presentation_evidence_state(source_status: str | None) -> EvidenceState:
    """Translate legacy/catalog status into the explicit presentation vocabulary.

    This is presentation classification only. It does not admit a product into
    engineering calculations and never upgrades evidence to VERIFIED.
    """
    status = (source_status or "").strip().upper()
    if status == EvidenceState.VERIFIED.value:
        return EvidenceState.VERIFIED
    if status == EvidenceState.ACCEPTED_FOR_CALCULATION.value:
        return EvidenceState.ACCEPTED_FOR_CALCULATION
    if status == EvidenceState.REJECTED.value:
        return EvidenceState.REJECTED
    if status in {"MISSING", "INPUT_REQUIRED"}:
        return EvidenceState.INPUT_REQUIRED
    return EvidenceState.DECLARED
