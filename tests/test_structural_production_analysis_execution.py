from lat_ces.building.floor_plan import FloorPlan, Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level
from lat_ces.structural.beam_solver import SimplySupportedBeamInput
from lat_ces.structural.production_analysis_execution import (
    ProductionStructuralAnalysisRequest,
    ProductionStructuralResultBinding,
    run_production_structural_analysis,
)


def test_production_model_executes_existing_solver_and_preserves_identity() -> None:
    model = BuildingModel(name="Production execution test")
    level = Level(name="Ground floor", elevation=0.0, height=3.0)
    floor_plan = FloorPlan(name="Ground floor plan")
    wall = Wall(
        name="Load-bearing wall",
        segment=Segment2D(Point2D(0.0, 0.0), Point2D(6.0, 0.0)),
        thickness=0.25,
        load_bearing=True,
        exterior=True,
        room_ids=("room-1",),
    )
    floor_plan.add_wall(wall)
    level.set_floor_plan(floor_plan)
    model.add_level(level)

    request = ProductionStructuralAnalysisRequest(
        model=model,
        beam=SimplySupportedBeamInput(
            span_m=6.0,
            uniform_load_n_m=10_000.0,
            youngs_modulus_pa=210e9,
            second_moment_m4=8e-5,
        ),
        result_id="production-structural-001",
        station_positions_m=(0.0, 3.0, 6.0),
    )

    before = dict(model.__dict__)
    binding = run_production_structural_analysis(request)

    assert isinstance(binding, ProductionStructuralResultBinding)
    assert binding.model is model
    assert binding.result.result_id == "production-structural-001"
    assert binding.result.solver_status == "SOLVER_CONVERGED"
    assert binding.result.reaction_left_n == 30_000.0
    assert binding.result.reaction_right_n == 30_000.0
    assert binding.result.max_bending_moment_nm == 45_000.0
    assert len(binding.result.stations) == 3
    assert binding.result.stations[1].bending_moment_nm == 45_000.0
    assert not hasattr(model, "VALID")
    assert model.__dict__ == before
