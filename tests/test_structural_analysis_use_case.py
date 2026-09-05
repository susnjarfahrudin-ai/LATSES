from lat_ces.building_model import BuildingModel
from lat_ces.structural.analysis_use_case import (
    StructuralAnalysisInput,
    run_structural_analysis,
)
from lat_ces.structural.beam_solver import SimplySupportedBeamInput


def test_run_structural_analysis_executes_benchmark_and_binds_canonical_result():
    model = BuildingModel()
    beam = SimplySupportedBeamInput(
        span_m=6.0,
        uniform_load_n_m=10_000.0,
        youngs_modulus_pa=210e9,
        second_moment_m4=8e-5,
    )

    binding = run_structural_analysis(
        StructuralAnalysisInput(
            model=model,
            beam=beam,
            result_id="structural-beam-use-case-001",
            station_positions_m=(0.0, 3.0, 6.0),
        )
    )

    result = model.structural_results[binding.result_id]
    assert binding.model is model
    assert result.solver_status == "SOLVER_CONVERGED"
    assert result.reaction_left_n == 30_000.0
    assert result.reaction_right_n == 30_000.0
    assert result.max_bending_moment_nm == 45_000.0
    assert len(result.stations) == 3
    assert result.stations[1].bending_moment_nm == 45_000.0
    assert not hasattr(model, "VALID")
