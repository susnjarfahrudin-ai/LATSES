from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .governance import IntegrityTrustEngine, ScientificArtifact


@dataclass(frozen=True)
class BuildingScientificResult:
    """Explicit bridge from validated scientific artifacts into BuildingModel consumers."""

    artifact_id: str
    sci_id: str
    kind: str
    version: int
    state: str
    content: dict[str, Any]
    provenance: tuple[str, ...]
    uncertainty: float | None
    content_hash: str


def to_building_result(artifact: ScientificArtifact) -> BuildingScientificResult:
    """Reject untrusted scientific output before it crosses into the building layer."""
    IntegrityTrustEngine().require_valid(artifact)
    if not artifact.provenance:
        raise ValueError("Scientific artifact cannot enter BuildingModel without provenance")
    if artifact.state.value not in {"VALIDATED", "APPROVED"}:
        raise ValueError("Only validated/approved scientific artifacts may enter BuildingModel")
    return BuildingScientificResult(
        artifact_id=artifact.artifact_id,
        sci_id=artifact.sci_id,
        kind=artifact.kind,
        version=artifact.version,
        state=artifact.state.value,
        content=dict(artifact.content),
        provenance=tuple(artifact.provenance),
        uncertainty=artifact.uncertainty,
        content_hash=artifact.content_hash,
    )
