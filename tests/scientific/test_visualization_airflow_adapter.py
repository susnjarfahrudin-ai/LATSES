from dataclasses import replace

from lat_ces.visualization_airflow_adapter import to_airflow_visualization_data
from lat_ces.visualization_contract import VisualizationRepresentation


def test_airflow_adapter_is_read_only_and_preserves_representation_data():
    representation = VisualizationRepresentation(
        representation_id="VIS-001",
        engineering_result_id="RESULT-001",
        building_model_id="BUILDING-001",
        quantity="air_velocity",
        value=0.32,
        unit="m/s",
        provenance_ref="MEAS-001",
        source_ref="MEAS-001",
        visualization_attributes={"layer": "airflow", "visible": True},
        status="VALID",
    )
    before = replace(representation)

    view_data = to_airflow_visualization_data(representation)

    assert view_data.representation_id == "VIS-001"
    assert view_data.building_model_id == "BUILDING-001"
    assert view_data.quantity == "air_velocity"
    assert view_data.value == 0.32
    assert view_data.unit == "m/s"
    assert view_data.provenance_ref == "MEAS-001"
    assert view_data.source_ref == "MEAS-001"
    assert view_data.visualization_attributes == {"layer": "airflow", "visible": True}
    assert representation == before
