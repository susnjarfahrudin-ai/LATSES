"""Convert the proven beam solver result into canonical structural storage."""
from __future__ import annotations

from lat_ces.structural.beam_solver import BeamSolverResult

from .canonical_result import CanonicalStructuralResult


def canonicalize_beam_solver_result(
    solver_result: BeamSolverResult,
    *,
    result_id: str,
    solver_provenance: str,
) -> CanonicalStructuralResult:
    """Convert solver evidence without changing its status or validation semantics."""
    if not isinstance(solver_result, BeamSolverResult):
        raise TypeError("solver_result must be a BeamSolverResult")

    return CanonicalStructuralResult(
        result_id=result_id,
        solver_status=solver_result.status,
        solver_provenance=solver_provenance,
        reaction_left_n=solver_result.reaction_left_n,
        reaction_right_n=solver_result.reaction_right_n,
        max_shear_n=solver_result.max_shear_n,
        max_bending_moment_nm=solver_result.max_bending_moment_nm,
        max_deflection_m=solver_result.max_deflection_m,
    )


__all__ = ["canonicalize_beam_solver_result"]
