"""Canonical structural solver result stored by the BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from lat_ces.structural.beam_solver import BeamSolverResult, SimplySupportedBeamInput


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


def canonicalize_beam_solver_result(
    result_id: str,
    beam: SimplySupportedBeamInput,
    solver_result: BeamSolverResult,
    *,
    solver_provenance: str = "SimplySupportedBeamInput/solve_simply_supported_beam_udl",
    station_positions_m: Tuple[float, ...] = (),
) -> CanonicalStructuralResult:
    """Convert one proven beam solver result into immutable canonical evidence."""
    if not isinstance(beam, SimplySupportedBeamInput):
        raise TypeError("beam must be a SimplySupportedBeamInput")
    if not isinstance(solver_result, BeamSolverResult):
        raise TypeError("solver_result must be a BeamSolverResult")

    stations = tuple(
        StructuralStationResult(
            x_m=x_m,
            shear_n=solver_result.shear_force_n(x_m, beam),
            bending_moment_nm=solver_result.bending_moment_nm(x_m, beam),
            deflection_m=solver_result.deflection_m(x_m, beam),
        )
        for x_m in station_positions_m
    )

    return CanonicalStructuralResult(
        result_id=result_id,
        solver_status=solver_result.status,
        solver_provenance=solver_provenance,
        reaction_left_n=solver_result.reaction_left_n,
        reaction_right_n=solver_result.reaction_right_n,
        max_shear_n=solver_result.max_shear_n,
        max_bending_moment_nm=solver_result.max_bending_moment_nm,
        max_deflection_m=solver_result.max_deflection_m,
        stations=stations,
    )


__all__ = [
    "StructuralStationResult",
    "CanonicalStructuralResult",
    "canonicalize_beam_solver_result",
]
