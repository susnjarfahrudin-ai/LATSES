from dataclasses import FrozenInstanceError

import pytest

from lat_ces.building_model import BuildingModel
from lat_ces.structural.canonical_result import CanonicalStructuralResult


def _result():
    return CanonicalStructuralResult(
        result_id="beam-benchmark-1",
        solver_status="SOLVER_CONVERGED",
        solver_provenance="SimplySupportedBeamInput/solve_simply_supported_beam_udl",
        reaction_left_n=30_000.0,
        reaction_right_n=30_000.0,
        max_shear_n=30_000.0,
        max_bending_moment_nm=45_000.0,
        max_deflection_m=0.010044642857,
    )


def test_canonical_result_is_stored_on_exact_building_model_instance():
    model = BuildingModel(name="Canonical structural result test")
    result = _result()

    model.add_structural_result(result)

    assert model.structural_results["beam-benchmark-1"] is result
    assert model.structural_results["beam-benchmark-1"].solver_status == "SOLVER_CONVERGED"


def test_solver_converged_is_not_valid():
    result = _result()

    assert result.solver_status == "SOLVER_CONVERGED"
    assert result.solver_status != "VALID"

    with pytest.raises(FrozenInstanceError):
        result.solver_status = "VALID"
