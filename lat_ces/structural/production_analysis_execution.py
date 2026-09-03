"""Execute deterministic structural analysis from the production BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.model import BuildingModel
from lat_ces.structural.beam_solver import SimplySupportedBeamInput, solve_simply_supported_beam_udl
from lat_ces.structural.canonical_result import (
    CanonicalStructuralResult,
    canonicalize_beam_solver_result,
)
from lat_ces.structural.production_analysis_bridge import ProductionStructuralAnalysisInput


@dataclass(frozen=True)
class ProductionStructuralResultBinding:
    """Immutable binding of one canonical result to the exact production model."""

    model: BuildingModel
    result: CanonicalStructuralResult


def run_production_structural_analysis(
    analysis_input: ProductionStructuralAnalysisInput,
) -> ProductionStructuralResultBinding:
    """Run the existing deterministic solver and bind its canonical result to the production model identity."""
    if not isinstance(analysis_input, ProductionStructuralAnalysisInput):
        raise TypeError("analysis_input must be a ProductionStructuralAnalysisInput")

    solver_result = solve_simply_supported_beam_udl(analysis_input.beam)
    canonical_result = canonicalize_beam_solver_result(
        analysis_input.result_id,
        analysis_input.beam,
        solver_result,
        solver_provenance=analysis_input.solver_provenance,
        station_positions_m=analysis_input.station_positions_m,
    )
    return ProductionStructuralResultBinding(
        model=analysis_input.model,
        result=canonical_result,
    )


__all__ = ["ProductionStructuralResultBinding", "run_production_structural_analysis"]
