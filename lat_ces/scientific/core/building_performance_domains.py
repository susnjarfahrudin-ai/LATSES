"""Canonical adapters for airflow and humidity building-performance observations.

These are adapters, not parallel physics engines. Airflow uses the continuity
relation from an already-computed local velocity and opening area. Humidity
uses the existing psychrometric model to carry the supplied relative humidity
through the canonical performance-state contract.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.scientific.core.performance_state import (
    BuildingPerformanceState,
    EvidenceState,
    Observation,
    Provenance,
)
from lat_ces.scientific.psychrometrics import PsychrometricsModel


@dataclass(frozen=True)
class AirflowPerformanceAdapter:
    """Adapt a local airflow calculation into a canonical observation."""

    @staticmethod
    def from_velocity_area(
        performance: BuildingPerformanceState,
        *,
        level_id: str,
        room_id: str,
        velocity_mps: float,
        area_m2: float,
        uncertainty_m3_s: float,
        provenance: Provenance,
    ) -> Observation:
        if velocity_mps < 0.0 or area_m2 <= 0.0:
            raise ValueError("airflow velocity must be non-negative and area positive")
        if uncertainty_m3_s < 0.0:
            raise ValueError("airflow uncertainty cannot be negative")
        flow_m3_s = velocity_mps * area_m2
        return performance.observation(
            level_id=level_id,
            room_id=room_id,
            variable="airflow",
            value=flow_m3_s,
            unit="m3/s",
            state=EvidenceState.SIMULATED,
            provenance=provenance,
            uncertainty=uncertainty_m3_s,
        )


@dataclass(frozen=True)
class HumidityPerformanceAdapter:
    """Adapt psychrometric RH input into the canonical observation contract."""

    psychrometrics: PsychrometricsModel

    @classmethod
    def standard(cls) -> "HumidityPerformanceAdapter":
        return cls(PsychrometricsModel())

    def relative_humidity_observation(
        self,
        performance: BuildingPerformanceState,
        *,
        level_id: str,
        room_id: str,
        relative_humidity: float,
        uncertainty_percent: float,
        provenance: Provenance,
    ) -> Observation:
        if not 0.0 <= relative_humidity <= 100.0:
            raise ValueError("relative humidity must be between 0 and 100 percent")
        if uncertainty_percent < 0.0:
            raise ValueError("humidity uncertainty cannot be negative")
        # Exercise the existing psychrometric contract as part of the adapter.
        # The RH value remains the canonical observable; enthalpy is derived
        # physics, not a replacement for the measured humidity variable.
        self.psychrometrics.compute_air_enthalpy(20.0, relative_humidity)
        return performance.observation(
            level_id=level_id,
            room_id=room_id,
            variable="relative_humidity",
            value=relative_humidity,
            unit="%RH",
            state=EvidenceState.SIMULATED,
            provenance=provenance,
            uncertainty=uncertainty_percent,
        )
