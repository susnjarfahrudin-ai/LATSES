"""Minimal OpenFOAM adapter boundary.

This module deliberately does not import, install, or execute OpenFOAM.
It converts a validated neutral external-backend package into a backend
request description that can later be consumed by an external process.
"""

from dataclasses import dataclass
from typing import Any, Mapping

from .package import ExternalBackendPackage, ExternalBackendPackageError


@dataclass(frozen=True)
class OpenFOAMRequest:
    """Immutable, neutral description of an OpenFOAM execution request."""

    package_id: str
    model_id: str
    model_revision: str
    case_format: str
    payload: Mapping[str, Any]


class OpenFOAMAdapter:
    """Pure boundary adapter; no OpenFOAM process or filesystem access."""

    backend_name = "OpenFOAM"
    case_format = "neutral-package"

    def prepare_request(self, package: ExternalBackendPackage) -> OpenFOAMRequest:
        if not isinstance(package, ExternalBackendPackage):
            raise TypeError("package must be an ExternalBackendPackage")

        snapshot = package.snapshot()
        provenance = snapshot["provenance"]
        if provenance["source"] != "LATSES":
            raise ExternalBackendPackageError(
                "OpenFOAM export must originate from LATSES"
            )

        return OpenFOAMRequest(
            package_id=snapshot["package_id"],
            model_id=snapshot["model_id"],
            model_revision=snapshot["model_revision"],
            case_format=self.case_format,
            payload=snapshot["payload"],
        )
