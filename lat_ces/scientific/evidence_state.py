from __future__ import annotations

from enum import Enum


class EvidenceState(str, Enum):
    """Epistemic status of evidence, independent of lifecycle or confidence."""

    DECLARED = "DECLARED"
    VERIFIED = "VERIFIED"
    MEASURED = "MEASURED"
    UNKNOWN = "UNKNOWN"


__all__ = ["EvidenceState"]
