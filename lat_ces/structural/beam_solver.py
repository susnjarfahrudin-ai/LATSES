"""Deterministic simply-supported beam benchmark.

This module is an isolated analytical solver used to establish a real static
calculation boundary before integrating structural results with BuildingModel.
It uses SI units throughout and does not alter the canonical building model.

Load case: uniform distributed load over the full span.
Boundary conditions: pin at x=0 and roller at x=L.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimplySupportedBeamInput:
    """SI input for a simply supported Euler-Bernoulli beam under UDL."""

    span_m: float
    uniform_load_n_m: float
    youngs_modulus_pa: float
    second_moment_m4: float

    def __post_init__(self) -> None:
        for name, value in (
            ("span_m", self.span_m),
            ("uniform_load_n_m", self.uniform_load_n_m),
            ("youngs_modulus_pa", self.youngs_modulus_pa),
            ("second_moment_m4", self.second_moment_m4),
        ):
            if value <= 0.0:
                raise ValueError(f"{name} must be > 0")


@dataclass(frozen=True)
class BeamSolverResult:
    """Analytical solution and equilibrium checks for the benchmark case."""

    status: str
    reaction_left_n: float
    reaction_right_n: float
    vertical_force_residual_n: float
    moment_residual_nm: float
    max_shear_n: float
    max_bending_moment_nm: float
    max_deflection_m: float

    def shear_force_n(self, x_m: float, beam: SimplySupportedBeamInput) -> float:
        """Internal shear V(x), positive upward on the left cut face."""
        _check_position(x_m, beam.span_m)
        return self.reaction_left_n - beam.uniform_load_n_m * x_m

    def bending_moment_nm(self, x_m: float, beam: SimplySupportedBeamInput) -> float:
        """Internal bending moment M(x) for 0 <= x <= L."""
        _check_position(x_m, beam.span_m)
        return self.reaction_left_n * x_m - beam.uniform_load_n_m * x_m**2 / 2.0

    def deflection_m(self, x_m: float, beam: SimplySupportedBeamInput) -> float:
        """Downward deflection magnitude for 0 <= x <= L under full-span UDL."""
        _check_position(x_m, beam.span_m)
        w = beam.uniform_load_n_m
        L = beam.span_m
        E = beam.youngs_modulus_pa
        I = beam.second_moment_m4
        return w * x_m * (L**3 - 2.0 * L * x_m**2 + x_m**3) / (24.0 * E * I)


def _check_position(x_m: float, span_m: float) -> None:
    if not 0.0 <= x_m <= span_m:
        raise ValueError("x_m must satisfy 0 <= x_m <= span_m")


def solve_simply_supported_beam_udl(beam: SimplySupportedBeamInput, *, tolerance: float = 1e-9) -> BeamSolverResult:
    """Solve the benchmark beam analytically and verify equilibrium."""
    if tolerance <= 0.0:
        raise ValueError("tolerance must be > 0")

    w = beam.uniform_load_n_m
    L = beam.span_m
    reaction = w * L / 2.0
    applied_resultant_n = w * L
    applied_moment_about_left_nm = applied_resultant_n * L / 2.0

    force_residual = reaction + reaction - applied_resultant_n
    moment_residual = reaction * L - applied_moment_about_left_nm

    max_shear = reaction
    max_moment = w * L**2 / 8.0
    max_deflection = 5.0 * w * L**4 / (384.0 * beam.youngs_modulus_pa * beam.second_moment_m4)

    converged = abs(force_residual) <= tolerance and abs(moment_residual) <= tolerance * max(1.0, applied_moment_about_left_nm)
    status = "SOLVER_CONVERGED" if converged else "SOLVER_FAILED"

    return BeamSolverResult(
        status=status,
        reaction_left_n=reaction,
        reaction_right_n=reaction,
        vertical_force_residual_n=force_residual,
        moment_residual_nm=moment_residual,
        max_shear_n=max_shear,
        max_bending_moment_nm=max_moment,
        max_deflection_m=max_deflection,
    )


__all__ = [
    "BeamSolverResult",
    "SimplySupportedBeamInput",
    "solve_simply_supported_beam_udl",
]
