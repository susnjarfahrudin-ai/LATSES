import pytest

from lat_ces.external_backend.openfoam_adapter import OpenFOAMAdapter
from lat_ces.external_backend.package import (
    ExternalBackendPackage,
    ExternalBackendPackageError,
)


def valid_package(**overrides):
    payload = {
        "schema": "latces.external_backend.package",
        "schema_version": "1.0",
        "package_id": "pkg-adversarial-001",
        "model_id": "model-001",
        "model_revision": "rev-001",
        "created_at": "2026-09-13T00:00:00Z",
        "units": {"length": "m", "mass": "kg", "time": "s"},
        "coordinate_system": {
            "name": "LOCAL_CARTESIAN_XYZ",
            "handedness": "right",
        },
        "provenance": {
            "source": "LATSES",
            "source_kind": "CANONICAL_BUILDING_MODEL",
            "evidence_state": "UNKNOWN",
        },
        "payload": {"objects": [{"id": "wall-1"}]},
    }
    payload.update(overrides)
    return payload


def test_openfoam_request_preserves_units_coordinates_and_provenance():
    package = ExternalBackendPackage(**valid_package())
    request = OpenFOAMAdapter().prepare_request(package)

    assert request.units == {"length": "m", "mass": "kg", "time": "s"}
    assert request.coordinate_system == {
        "name": "LOCAL_CARTESIAN_XYZ",
        "handedness": "right",
    }
    assert request.provenance == {
        "source": "LATSES",
        "source_kind": "CANONICAL_BUILDING_MODEL",
        "evidence_state": "UNKNOWN",
    }


def test_openfoam_package_rejects_missing_required_units():
    with pytest.raises(ExternalBackendPackageError):
        ExternalBackendPackage(
            **valid_package(units={"length": "m", "mass": "kg"})
        )


def test_openfoam_package_rejects_missing_coordinate_identity():
    with pytest.raises(ExternalBackendPackageError):
        ExternalBackendPackage(
            **valid_package(coordinate_system={"name": "LOCAL_CARTESIAN_XYZ"})
        )


def test_openfoam_request_preserves_unknown_payload_without_fabrication():
    package = ExternalBackendPackage(
        **valid_package(
            payload={
                "objects": [{"id": "wall-1"}],
                "evidence_state": "UNKNOWN",
                "unverified_input": {"velocity_mps": None},
            }
        )
    )

    request = OpenFOAMAdapter().prepare_request(package)

    assert request.payload == {
        "objects": [{"id": "wall-1"}],
        "evidence_state": "UNKNOWN",
        "unverified_input": {"velocity_mps": None},
    }


def test_openfoam_adapter_is_outbound_only():
    adapter = OpenFOAMAdapter()

    assert hasattr(adapter, "prepare_request")
    assert not hasattr(adapter, "execute")
    assert not hasattr(adapter, "import_result")
