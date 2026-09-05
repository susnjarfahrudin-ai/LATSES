"""Runtime observation seam for RCI-AD telemetry.

This module only collects host telemetry and forwards the immutable snapshot to
an optional observer. It does not make policy decisions, throttle work, or
modify runtime state.
"""

from __future__ import annotations

from typing import Callable

from .telemetry import HostTelemetry, collect_host_telemetry

TelemetryObserver = Callable[[HostTelemetry], None]


def observe_host_telemetry(
    observer: TelemetryObserver,
    *,
    interval: float = 0.05,
) -> HostTelemetry:
    """Collect one host snapshot, forward it, and return the same snapshot."""
    telemetry = collect_host_telemetry(interval=interval)
    observer(telemetry)
    return telemetry
