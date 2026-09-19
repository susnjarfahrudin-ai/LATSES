"""Read-only host-wide RCI-AD observation coordinator."""
from __future__ import annotations
from dataclasses import dataclass
from .telemetry import HostTelemetry,collect_host_telemetry
from .universal_io import InterfaceObservation
from .resource_model import interface_pressure

@dataclass(frozen=True)
class HostObservation:
    telemetry: HostTelemetry
    interfaces: tuple[InterfaceObservation,...]

class HostObservationPlane:
    def observe(self, interfaces=()):
        return HostObservation(collect_host_telemetry(interval=0),tuple(interfaces))
