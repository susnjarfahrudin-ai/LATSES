"""Neutral, immutable external-backend package contract."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


class ExternalBackendPackageError(ValueError):
    """Raised when a neutral external-backend package violates its contract."""


@dataclass(frozen=True)
class ExternalBackendPackage:
    """Read-only snapshot exchanged across the external-backend boundary."""

    schema: str
    schema_version: str
    package_id: str
    model_id: str
    model_revision: str
    created_at: str
    units: Mapping[str, str]
    coordinate_system: Mapping[str, str]
    provenance: Mapping[str, str]
    payload: Mapping[str, Any]

    REQUIRED_UNITS = ("length", "mass", "time")
    REQUIRED_COORDINATE_FIELDS = ("name", "handedness")
    REQUIRED_PROVENANCE_FIELDS = ("source", "source_kind", "evidence_state")
    SCHEMA = "latces.external_backend.package"

    def __post_init__(self) -> None:
        for name in (
            "schema",
            "schema_version",
            "package_id",
            "model_id",
            "model_revision",
            "created_at",
        ):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ExternalBackendPackageError(f"{name} must be a non-empty string")

        if self.schema != self.SCHEMA:
            raise ExternalBackendPackageError("unsupported schema identifier")

        self._require_mapping("units", self.units, self.REQUIRED_UNITS)
        self._require_mapping("coordinate_system", self.coordinate_system, self.REQUIRED_COORDINATE_FIELDS)
        self._require_mapping("provenance", self.provenance, self.REQUIRED_PROVENANCE_FIELDS)
        if not isinstance(self.payload, Mapping):
            raise ExternalBackendPackageError("payload must be a mapping")

        object.__setattr__(self, "units", MappingProxyType(dict(self.units)))
        object.__setattr__(self, "coordinate_system", MappingProxyType(dict(self.coordinate_system)))
        object.__setattr__(self, "provenance", MappingProxyType(dict(self.provenance)))
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))

    @staticmethod
    def _require_mapping(name: str, value: Mapping[str, str], required: tuple[str, ...]) -> None:
        if not isinstance(value, Mapping):
            raise ExternalBackendPackageError(f"{name} must be a mapping")
        missing = [key for key in required if key not in value or not isinstance(value[key], str) or not value[key].strip()]
        if missing:
            raise ExternalBackendPackageError(f"{name} missing required fields: {', '.join(missing)}")

    def snapshot(self) -> dict[str, Any]:
        """Return a detached neutral-data representation for serialization."""
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "package_id": self.package_id,
            "model_id": self.model_id,
            "model_revision": self.model_revision,
            "created_at": self.created_at,
            "units": dict(self.units),
            "coordinate_system": dict(self.coordinate_system),
            "provenance": dict(self.provenance),
            "payload": dict(self.payload),
        }
