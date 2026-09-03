"""Deterministic structural analysis use case for the beam benchmark."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.model import BuildingModel
from lat_ces.structural.beam_solver import SimplySupportedBeamInput, solve_simply_supported_beam_udl
from lat_ces.structural.canonical_binding import (
    CanonicalStructuralResultBinding,
    attach_canonical_structural_result,
)
from lat_ces.structural.canonical_result import canonicalize_beam_solver_result


@dataclass(frozen=True)
class StructuralAnalysisInput:
    """Explicit input boundary for one deterministic structural analysis."""

    model: BuildingModel
    beam: SimplySupportedBeamInput
    result_id: str
    solver_provenance: str = "benchmark/simply-supported-beam-udl"
    station_positions_m: tuple[float, ...] = ()


def run_structural_analysis(
    analysis_input: StructuralAnalysisInput,
) -> CanonicalStructuralResultBinding:
    """Execute the existing beam solver and bind its canonical result to the model."""
    if not isinstance(analysis_input, StructuralAnalysisInput):
        raise TypeError("analysis_input must be a StructuralAnalysisInput")

    solver_result = solve_simply_supported_beam_udl(analysis_input.beam)
    canonical_result = canonicalize_beam_solver_result(
        analysis_input.result_id,
        analysis_input.beam,
        solver_result,
        solver_provenance=analysis_input.solver_provenance,
        station_positions_m=analysis_input.station_positions_m,
    )
    return attach_canonical_structural_result(analysis_input.model, canonical_result)


__all__ = ["StructuralAnalysisInput", "run_structural_analysis"]
