"""Canonical structural solver result stored by the BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StructuralStationResult:
    """Solver evidence at one canonical beam station."""

    x_m: float
    shear_n: float
    bending_moment_nm: float
    deflection_m: float


@dataclass(frozen=True)
class CanonicalStructuralResult:
    """Immutable structural result preserved independently of validation semantics."""

    result_id: str
    solver_status: str
    solver_provenance: str
    reaction_left_n: float
    reaction_right_n: float
    max_shear_n: float
    max_bending_moment_nm: float
    max_deflection_m: float
    stations: Tuple[StructuralStationResult, ...] = ()

    def __post_init__(self) -> None:
        if not self.result_id.strip():
            raise ValueError("result_id cannot be empty")
        if not self.solver_status.strip():
            raise ValueError("solver_status cannot be empty")
        if not self.solver_provenance.strip():
            raise ValueError("solver_provenance cannot be empty")
        if not isinstance(self.stations, tuple):
            raise TypeError("stations must be a tuple")


__all__ = ["StructuralStationResult", "CanonicalStructuralResult"]
