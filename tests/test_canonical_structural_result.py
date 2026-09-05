from dataclasses import FrozenInstanceError

import pytest

from lat_ces.building_model import BuildingModel
from lat_ces.structural.beam_solver import (
    SimplySupportedBeamInput,
    solve_simply_supported_beam_udl,
)
from lat_ces.structural.canonical_result import (
    CanonicalStructuralResult,
    canonicalize_beam_solver_result,
)


def _beam_and_result():
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8e-5,
    )
    return beam, solve_simply_supported_beam_udl(beam)


def test_canonical_result_is_stored_on_exact_building_model_instance():
    model = BuildingModel(name="Canonical structural result test")
    result = CanonicalStructuralResult(
        result_id="beam-benchmark-1",
        solver_status="SOLVER_CONVERGED",
        solver_provenance="test",
        reaction_left_n=30_000.0,
        reaction_right_n=30_000.0,
        max_shear_n=30_000.0,
        max_bending_moment_nm=45_000.0,
        max_deflection_m=0.010044642857,
    )

    model.add_structural_result(result)

    assert model.structural_results["beam-benchmark-1"] is result


def test_solver_result_maps_to_canonical_result_without_changing_status():
    beam, solver_result = _beam_and_result()

    result = canonicalize_beam_solver_result(
        "beam-benchmark-1",
        beam,
        solver_result,
        station_positions_m=(0.0, 3.0, 6.0),
    )

    assert result.solver_status == "SOLVER_CONVERGED"
    assert result.solver_status != "VALID"
    assert result.reaction_left_n == solver_result.reaction_left_n
    assert result.reaction_right_n == solver_result.reaction_right_n
    assert result.max_bending_moment_nm == solver_result.max_bending_moment_nm
    assert len(result.stations) == 3
    assert result.stations[1].bending_moment_nm == pytest.approx(45_000.0)
    assert result.stations[1].deflection_m == pytest.approx(solver_result.max_deflection_m)


def test_canonical_result_is_immutable_and_does_not_become_valid():
    beam, solver_result = _beam_and_result()
    result = canonicalize_beam_solver_result("beam-benchmark-1", beam, solver_result)

    assert result.solver_status == "SOLVER_CONVERGED"
    assert result.solver_status != "VALID"

    with pytest.raises(FrozenInstanceError):
        result.solver_status = "VALID"
