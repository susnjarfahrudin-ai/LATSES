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
        "package_id": "pkg-001",
        "model_id": "model-001",
        "model_revision": "rev-001",
        "units": {"length": "m"},
        "coordinate_system": "LOCAL_CARTESIAN_XYZ",
        "provenance": {
            "source": "LATSES",
            "source_kind": "CANONICAL_BUILDING_MODEL",
            "evidence_state": "VERIFIED",
        },
        "payload": {"objects": [{"id": "wall-1"}]},
    }
    payload.update(overrides)
    return payload


def test_openfoam_request_is_detached_from_package_payload():
    package = ExternalBackendPackage(**valid_package())
    request = OpenFOAMAdapter().prepare_request(package)

    with pytest.raises(TypeError):
        request.payload["objects"] = []

    snapshot = package.snapshot()
    assert snapshot["payload"] == {"objects": [{"id": "wall-1"}]}


def test_openfoam_adapter_rejects_non_latses_provenance():
    package = ExternalBackendPackage(
        **valid_package(
            provenance={
                "source": "OPENFOAM",
                "source_kind": "EXTERNAL_BACKEND",
                "evidence_state": "VERIFIED",
            }
        )
    )

    with pytest.raises(ExternalBackendPackageError):
        OpenFOAMAdapter().prepare_request(package)


def test_openfoam_adapter_rejects_untrusted_backend_as_canonical_source():
    package = ExternalBackendPackage(
        **valid_package(
            provenance={
                "source": "BLENDER",
                "source_kind": "EXTERNAL_BACKEND",
                "evidence_state": "VERIFIED",
            }
        )
    )

    with pytest.raises(ExternalBackendPackageError):
        OpenFOAMAdapter().prepare_request(package)


def test_openfoam_request_preserves_identity_and_revision():
    package = ExternalBackendPackage(**valid_package())
    request = OpenFOAMAdapter().prepare_request(package)

    assert request.package_id == "pkg-001"
    assert request.model_id == "model-001"
    assert request.model_revision == "rev-001"
    assert request.case_format == "neutral-package"
