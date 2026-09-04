from lat_ces.building_model import BuildingModel
from lat_ces.structural.beam_solver import (
    SimplySupportedBeamInput,
    solve_simply_supported_beam_udl,
)
from lat_ces.structural.building_model_bridge import bind_solver_result


def _benchmark_result():
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8e-5,
    )
    return solve_simply_supported_beam_udl(beam)


def test_bridge_preserves_canonical_model_identity_and_solver_result():
    model = BuildingModel(name="Bridge test")
    result = _benchmark_result()

    binding = bind_solver_result(model, result)

    assert binding.model is model
    assert binding.solver_result is result
    assert binding.solver_result.status == "SOLVER_CONVERGED"
    assert binding.solver_converged is True


def test_bridge_does_not_mutate_building_model_state():
    model = BuildingModel(name="Bridge test")
    before = dict(model.__dict__)

    bind_solver_result(model, _benchmark_result())

    assert model.__dict__ == before
