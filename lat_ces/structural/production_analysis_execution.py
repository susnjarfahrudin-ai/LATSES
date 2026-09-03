"""Execute deterministic structural analysis from the production BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building.model import BuildingModel
from lat_ces.structural.beam_solver import SimplySupportedBeamInput, solve_simply_supported_beam_udl
from lat_ces.structural.canonical_result import (
    CanonicalStructuralResult,
    canonicalize_beam_solver_result,
)
from lat_ces.structural.production_analysis_bridge import to_production_structural_input


@dataclass(frozen=True)
class ProductionStructuralAnalysisRequest:
    """Immutable execution request rooted in the production canonical model."""

    model: BuildingModel
    beam: SimplySupportedBeamInput
    result_id: str
    solver_provenance: str = "production/simply-supported-beam-udl"
    station_positions_m: tuple[float, ...] = ()


@dataclass(frozen=True)
class ProductionStructuralResultBinding:
    """Immutable binding of one canonical result to the exact production model."""

    model: BuildingModel
    result: CanonicalStructuralResult


def run_production_structural_analysis(
    request: ProductionStructuralAnalysisRequest,
) -> ProductionStructuralResultBinding:
    """Run the existing solver and bind its canonical result to the same production model instance."""
    if not isinstance(request, ProductionStructuralAnalysisRequest):
        raise TypeError("request must be a ProductionStructuralAnalysisRequest")

    production_input = to_production_structural_input(request.model)
    if production_input.model is not request.model:
        raise RuntimeError("production model identity was not preserved")

    solver_result = solve_simply_supported_beam_udl(request.beam)
    canonical_result = canonicalize_beam_solver_result(
        request.result_id,
        request.beam,
        solver_result,
        solver_provenance=request.solver_provenance,
        station_positions_m=request.station_positions_m,
    )
    return ProductionStructuralResultBinding(
        model=request.model,
        result=canonical_result,
    )


__all__ = [
    "ProductionStructuralAnalysisRequest",
    "ProductionStructuralResultBinding",
    "run_production_structural_analysis",
]
