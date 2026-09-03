"""Evidence-first validation result contract for the LAT-CES Umbrella."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UmbrellaResult:
    status: str
    message: str
    element_id: Optional[str] = None
    evidence: Optional[str] = None
    recommendation: Optional[str] = None

    def __post_init__(self) -> None:
        if self.status not in {"GREEN", "YELLOW", "RED"}:
            raise ValueError("status must be GREEN, YELLOW, or RED")
        if not self.message.strip():
            raise ValueError("message must not be empty")


def red(message: str, *, element_id: Optional[str] = None,
        evidence: Optional[str] = None,
        recommendation: Optional[str] = None) -> UmbrellaResult:
    return UmbrellaResult("RED", message, element_id, evidence, recommendation)
