from __future__ import annotations

import pytest

from lat_ces.structural.beam_solver import (
    SimplySupportedBeamInput,
    solve_simply_supported_beam_udl,
)


def test_simply_supported_beam_udl_benchmark() -> None:
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8.0e-5,
    )

    result = solve_simply_supported_beam_udl(beam)

    assert result.status == "SOLVER_CONVERGED"
    assert result.reaction_left_n == pytest.approx(30_000.0)
    assert result.reaction_right_n == pytest.approx(30_000.0)
    assert result.vertical_force_residual_n == pytest.approx(0.0, abs=1e-9)
    assert result.moment_residual_nm == pytest.approx(0.0, abs=1e-9)
    assert result.max_shear_n == pytest.approx(30_000.0)
    assert result.max_bending_moment_nm == pytest.approx(45_000.0)
    assert result.max_deflection_m == pytest.approx(0.010044642857142857, rel=1e-12)

    assert result.shear_force_n(0.0, beam) == pytest.approx(30_000.0)
    assert result.shear_force_n(beam.span_m / 2.0, beam) == pytest.approx(0.0)
    assert result.shear_force_n(beam.span_m, beam) == pytest.approx(-30_000.0)

    assert result.bending_moment_nm(0.0, beam) == pytest.approx(0.0)
    assert result.bending_moment_nm(beam.span_m / 2.0, beam) == pytest.approx(45_000.0)
    assert result.bending_moment_nm(beam.span_m, beam) == pytest.approx(0.0)

    assert result.deflection_m(0.0, beam) == pytest.approx(0.0)
    assert result.deflection_m(beam.span_m, beam) == pytest.approx(0.0)
    assert result.deflection_m(beam.span_m / 2.0, beam) == pytest.approx(result.max_deflection_m)
