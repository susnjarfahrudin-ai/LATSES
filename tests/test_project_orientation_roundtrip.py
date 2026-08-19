from lat_ces.building.model import BuildingModel
from lat_ces.building.orientation import BuildingOrientation
from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.workflow import BuildingWorkflow


def test_orientation_round_trip(tmp_path) -> None:
    model = BuildingModel(name="Orijentacija test", orientation=BuildingOrientation(127.5))
    workflow = BuildingWorkflow(model=model)
    path = save_workflow(workflow, tmp_path / "project.json")

    restored = load_workflow(path)

    assert restored.model.orientation.north_azimuth_deg == 127.5
    assert restored.project_spec is not None
    assert restored.project_spec.orientation.north_azimuth_deg == 127.5
