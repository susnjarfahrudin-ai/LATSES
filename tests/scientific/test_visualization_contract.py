from dataclasses import dataclass

from lat_ces.visualization_contract import VisualizationRepresentation


@dataclass
class SourceResult:
    building_model_id: str
    quantity: str
    value: float
    unit: str
    provenance_ref: str


def test_visualization_representation_preserves_canonical_result_data():
    source = SourceResult(
        building_model_id="BUILDING-001",
        quantity="air_velocity",
        value=0.32,
        unit="m/s",
        provenance_ref="measurement:MEAS-001",
    )
    before = source.__dict__.copy()

    representation = VisualizationRepresentation(
        representation_id="VIZ-001",
        source_ref="measurement:MEAS-001",
        building_model_id=source.building_model_id,
        quantity=source.quantity,
        value=source.value,
        unit=source.unit,
        provenance_ref=source.provenance_ref,
        visualization_attributes={
            "layer": "measurements",
            "geometry": "marker",
            "visible": True,
        },
    )

    assert representation.building_model_id == "BUILDING-001"
    assert representation.source_ref == "measurement:MEAS-001"
    assert representation.quantity == "air_velocity"
    assert representation.value == 0.32
    assert representation.unit == "m/s"
    assert representation.provenance_ref == "measurement:MEAS-001"
    assert representation.visualization_attributes["layer"] == "measurements"
    assert source.__dict__ == before


def test_visualization_representation_is_immutable():
    representation = VisualizationRepresentation(
        representation_id="VIZ-002",
        source_ref="result:RES-001",
        building_model_id="BUILDING-001",
        quantity="temperature",
        value=23.4,
        unit="degC",
        provenance_ref="simulation:SIM-001",
        visualization_attributes={"layer": "thermal"},
    )

    try:
        representation.value = 99.0
    except Exception:
        pass
    else:
        raise AssertionError("VisualizationRepresentation must be immutable")
