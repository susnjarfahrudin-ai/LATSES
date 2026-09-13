from lat_ces.external_backend.openfoam_adapter import OpenFOAMAdapter
from lat_ces.external_backend.package import ExternalBackendPackage


def valid_package():
    return ExternalBackendPackage(
        schema="latces.external_backend.package",
        schema_version="1.0",
        package_id="pkg-boundary-001",
        model_id="model-001",
        model_revision="rev-001",
        created_at="2026-09-13T00:00:00Z",
        units={"length": "m", "mass": "kg", "time": "s"},
        coordinate_system={"name": "LOCAL_CARTESIAN_XYZ", "handedness": "right"},
        provenance={
            "source": "LATSES",
            "source_kind": "CANONICAL_BUILDING_MODEL",
            "evidence_state": "UNKNOWN",
        },
        payload={"objects": [{"id": "wall-1"}]},
    )


def fake_external_process(request):
    """Test-only stand-in for an external solver/process."""
    return {
        "schema": "latces.external_backend.result",
        "schema_version": "1.0",
        "package_id": request.package_id,
        "model_id": request.model_id,
        "model_revision": request.model_revision,
        "units": dict(request.units),
        "coordinate_system": dict(request.coordinate_system),
        "provenance": {
            "source": "FAKE_EXTERNAL_PROCESS",
            "source_kind": "EXTERNAL_RESULT",
            "evidence_state": "UNKNOWN",
        },
        "payload": {"claim": "velocity_mps=2.5", "evidence_state": "UNKNOWN"},
    }


def test_external_result_crosses_boundary_as_neutral_data_only():
    request = OpenFOAMAdapter().prepare_request(valid_package())
    external_result = fake_external_process(request)

    assert external_result["package_id"] == request.package_id
    assert external_result["model_id"] == request.model_id
    assert external_result["model_revision"] == request.model_revision
    assert external_result["provenance"]["source"] == "FAKE_EXTERNAL_PROCESS"
    assert external_result["provenance"]["evidence_state"] == "UNKNOWN"
    assert external_result["payload"]["evidence_state"] == "UNKNOWN"


def test_external_result_cannot_become_validated_engineering_result_implicitly():
    adapter = OpenFOAMAdapter()
    request = adapter.prepare_request(valid_package())
    external_result = fake_external_process(request)

    assert isinstance(external_result, dict)
    assert not hasattr(adapter, "import_result")
    assert not hasattr(adapter, "validate_result")


def test_adversarial_external_claim_of_validation_remains_untrusted():
    request = OpenFOAMAdapter().prepare_request(valid_package())
    external_result = fake_external_process(request)
    external_result["provenance"]["evidence_state"] = "VERIFIED"
    external_result["payload"]["evidence_state"] = "VERIFIED"
    external_result["payload"]["claim"] = "validated_engineering_result=true"

    assert external_result["provenance"]["source"] == "FAKE_EXTERNAL_PROCESS"
    assert external_result["provenance"]["evidence_state"] == "VERIFIED"
    assert external_result["payload"]["claim"] == "validated_engineering_result=true"
    assert not hasattr(OpenFOAMAdapter(), "import_result")
