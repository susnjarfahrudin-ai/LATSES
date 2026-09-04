"""Explicit binding of canonical structural results to a BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building_model.core import BuildingModel
from lat_ces.structural.canonical_result import CanonicalStructuralResult


@dataclass(frozen=True)
class CanonicalStructuralResultBinding:
    """Immutable identity binding between a BuildingModel and result ID."""

    model: BuildingModel
    result_id: str


def attach_canonical_structural_result(
    model: BuildingModel,
    result: CanonicalStructuralResult,
) -> CanonicalStructuralResultBinding:
    """Store and explicitly bind one canonical result to the exact model instance."""
    if not isinstance(model, BuildingModel):
        raise TypeError("model must be a BuildingModel")
    if not isinstance(result, CanonicalStructuralResult):
        raise TypeError("result must be a CanonicalStructuralResult")

    model.add_structural_result(result)
    return CanonicalStructuralResultBinding(model=model, result_id=result.result_id)


__all__ = [
    "CanonicalStructuralResultBinding",
    "attach_canonical_structural_result",
]
