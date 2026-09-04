from dataclasses import FrozenInstanceError

import pytest

from lat_ces.building_model import BuildingModel
from lat_ces.structural.beam_solver import (
    SimplySupportedBeamInput,
    solve_simply_supported_beam_udl,
)
from lat_ces.structural.canonical_result import canonicalize_beam_solver_result
from lat_ces.structural.canonical_binding import attach_canonical_structural_result


def test_canonical_result_is_bound_to_exact_building_model_and_result_id():
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8e-5,
    )
    solver_result = solve_simply_supported_beam_udl(beam)
    result = canonicalize_beam_solver_result(
        "structural-beam-001",
        beam,
        solver_result,
        solver_provenance="benchmark/simply-supported-beam-udl",
        station_positions_m=(0.0, 3.0, 6.0),
    )
    model = BuildingModel()

    binding = attach_canonical_structural_result(model, result)

    assert binding.model is model
    assert binding.result_id == "structural-beam-001"
    assert model.structural_results[binding.result_id] is result
    assert result.solver_status == "SOLVER_CONVERGED"
    assert not hasattr(model, "VALID")


def test_binding_is_immutable_and_duplicate_result_ids_are_rejected():
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8e-5,
    )
    solver_result = solve_simply_supported_beam_udl(beam)
    result = canonicalize_beam_solver_result("structural-beam-002", beam, solver_result)
    model = BuildingModel()

    binding = attach_canonical_structural_result(model, result)

    with pytest.raises(FrozenInstanceError):
        binding.result_id = "VALID"

    with pytest.raises(ValueError, match="duplicate structural result id"):
        attach_canonical_structural_result(model, result)

    assert binding.model is model
    assert binding.result_id == "structural-beam-002"
    assert result.solver_status == "SOLVER_CONVERGED"
