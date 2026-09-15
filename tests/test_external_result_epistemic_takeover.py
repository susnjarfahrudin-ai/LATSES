import pytest

from lat_ces.external_backend.package import (
    ExternalBackendPackage,
    ExternalBackendPackageError,
)


def test_external_result_cannot_forge_a_verified_latces_package():
    """Adversarial proof: external claims must not become LATSES evidence implicitly."""
    external_result = {
        "schema": "latces.external_backend.result",
        "schema_version": "1.0",
        "package_id": "external-001",
        "model_id": "model-001",
        "model_revision": "rev-001",
        "created_at": "2026-09-13T00:00:00Z",
        "units": {"length": "m", "mass": "kg", "time": "s"},
        "coordinate_system": {"name": "LOCAL_CARTESIAN_XYZ", "handedness": "right"},
        "provenance": {
            "source": "FAKE_EXTERNAL_PROCESS",
            "source_kind": "EXTERNAL_RESULT",
            "evidence_state": "UNKNOWN",
        },
        "payload": {"claim": "validated_engineering_result=true"},
    }

    forged = dict(external_result)
    forged["schema"] = "latces.external_backend.package"
    forged["provenance"] = {
        "source": "LATSES",
        "source_kind": "CANONICAL_BUILDING_MODEL",
        "evidence_state": "VERIFIED",
    }

    with pytest.raises(ExternalBackendPackageError):
        ExternalBackendPackage(**forged)
