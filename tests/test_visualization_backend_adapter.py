from lat_ces.visualization_backend_adapter import to_visualization_backend_envelope
from lat_ces.visualization_contract import VisualizationRepresentation


def make_representation() -> VisualizationRepresentation:
    return VisualizationRepresentation(
        representation_id="VIS-001",
        source_ref="engineering-result-001",
        building_model_id="BM-001",
        quantity="air_velocity",
        value=0.35,
        unit="m/s",
        provenance_ref="prov-001",
        visualization_attributes={
            "location": (1.0, 2.0, 1.2),
            "sensor_id": "S-017",
            "layer": "flow",
        },
    )


def test_backend_umbrella_preserves_canonical_representation() -> None:
    representation = make_representation()

    for backend in ("blender", "paraview", "openfoam"):
        envelope = to_visualization_backend_envelope(representation, backend)

        assert envelope.backend == backend
        assert envelope.representation_id == representation.representation_id
        assert envelope.source_ref == representation.source_ref
        assert envelope.building_model_id == representation.building_model_id
        assert envelope.quantity == representation.quantity
        assert envelope.value == representation.value
        assert envelope.unit == representation.unit
        assert envelope.provenance_ref == representation.provenance_ref
        assert envelope.visualization_attributes == representation.visualization_attributes
        assert envelope.status == representation.status


def test_backend_umbrella_rejects_unknown_backend() -> None:
    representation = make_representation()

    try:
        to_visualization_backend_envelope(representation, "unknown")
    except ValueError as exc:
        assert "unsupported visualization backend" in str(exc)
    else:
        raise AssertionError("unknown backend must be rejected")
