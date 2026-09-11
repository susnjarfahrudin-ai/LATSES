import pytest

from lat_ces.external_backend import ExternalBackendPackage, ExternalBackendPackageError


def valid_package(**overrides):
    data = {
        "schema": "latces.external_backend.package",
        "schema_version": "1.0",
        "package_id": "pkg-001",
        "model_id": "house-001",
        "model_revision": "rev-7",
        "created_at": "2026-09-11T10:00:00+02:00",
        "units": {"length": "m", "mass": "kg", "time": "s"},
        "coordinate_system": {"name": "local-cartesian", "handedness": "right"},
        "provenance": {
            "source": "LATSES",
            "source_kind": "CANONICAL_BUILDING_MODEL",
            "evidence_state": "VERIFIED",
        },
        "payload": {"objects": []},
    }
    data.update(overrides)
    return data


def test_valid_package_is_constructed_and_serialization_is_detached():
    source_payload = {"objects": [{"id": "wall-1"}]}
    package = ExternalBackendPackage(**valid_package(payload=source_payload))

    source_payload["objects"].append({"id": "wall-2"})
    snapshot = package.snapshot()

    assert snapshot["payload"] == {"objects": [{"id": "wall-1"}]}
    assert snapshot["model_id"] == "house-001"
    assert snapshot["model_revision"] == "rev-7"


def test_package_is_immutable_at_boundary():
    package = ExternalBackendPackage(**valid_package())

    with pytest.raises(TypeError):
        package.model_id = "attacker-model"

    with pytest.raises(TypeError):
        package.units["length"] = "mm"


def test_missing_units_cannot_cross_boundary():
    units = {"length": "m", "mass": "kg"}

    with pytest.raises(ExternalBackendPackageError, match="units missing"):
        ExternalBackendPackage(**valid_package(units=units))


def test_missing_coordinate_semantics_cannot_cross_boundary():
    coordinates = {"name": "local-cartesian"}

    with pytest.raises(ExternalBackendPackageError, match="coordinate_system missing"):
        ExternalBackendPackage(**valid_package(coordinate_system=coordinates))


def test_missing_provenance_cannot_cross_boundary():
    provenance = {"source": "LATSES", "source_kind": "CANONICAL_BUILDING_MODEL"}

    with pytest.raises(ExternalBackendPackageError, match="provenance missing"):
        ExternalBackendPackage(**valid_package(provenance=provenance))


def test_unknown_values_are_not_replaced_by_adapter_defaults():
    payload = {"thermal_conductivity": None}
    package = ExternalBackendPackage(**valid_package(payload=payload))

    assert package.snapshot()["payload"]["thermal_conductivity"] is None


def test_external_result_is_not_marked_as_validated_by_package_boundary():
    package = ExternalBackendPackage(
        **valid_package(
            provenance={
                "source": "OpenFOAM",
                "source_kind": "EXTERNAL_BACKEND_RESULT",
                "evidence_state": "DECLARED",
            },
            payload={"pressure": 101325.0},
        )
    )

    assert package.provenance["source_kind"] == "EXTERNAL_BACKEND_RESULT"
    assert package.provenance["evidence_state"] == "DECLARED"
    assert package.provenance["evidence_state"] != "VERIFIED"


def test_schema_identity_cannot_be_silently_changed():
    with pytest.raises(ExternalBackendPackageError, match="unsupported schema"):
        ExternalBackendPackage(**valid_package(schema="other.package"))
