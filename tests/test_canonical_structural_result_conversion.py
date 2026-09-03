from lat_ces.structural.beam_solver import (
    SimplySupportedBeamInput,
    solve_simply_supported_beam_udl,
)
from lat_ces.structural.canonical_result import CanonicalStructuralResult
from lat_ces.structural.canonical_result_conversion import canonicalize_beam_solver_result


def _solver_result():
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8e-5,
    )
    return solve_simply_supported_beam_udl(beam)


def test_beam_solver_result_maps_verbatim_to_canonical_result():
    solver_result = _solver_result()

    result = canonicalize_beam_solver_result(
        solver_result,
        result_id="beam-benchmark-1",
        solver_provenance="SimplySupportedBeamInput/solve_simply_supported_beam_udl",
    )

    assert isinstance(result, CanonicalStructuralResult)
    assert result.result_id == "beam-benchmark-1"
    assert result.solver_status == solver_result.status == "SOLVER_CONVERGED"
    assert result.solver_status != "VALID"
    assert result.solver_provenance == "SimplySupportedBeamInput/solve_simply_supported_beam_udl"
    assert result.reaction_left_n == solver_result.reaction_left_n
    assert result.reaction_right_n == solver_result.reaction_right_n
    assert result.max_shear_n == solver_result.max_shear_n
    assert result.max_bending_moment_nm == solver_result.max_bending_moment_nm
    assert result.max_deflection_m == solver_result.max_deflection_m


def test_conversion_does_not_mutate_solver_result():
    solver_result = _solver_result()
    before = solver_result

    canonicalize_beam_solver_result(
        solver_result,
        result_id="beam-benchmark-2",
        solver_provenance="beam benchmark",
    )

    assert solver_result is before
    assert solver_result.status == "SOLVER_CONVERGED"
