"""Canonical simulation/measurement/validation state for building performance.

This module is deliberately independent of GUI concerns.  It provides the
small contract that connects the authoritative BuildingModel to predicted and
measured observations without conflating model output with evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import sqrt
from typing import Optional

from lat_ces.building_model.core import BuildingModel


class EvidenceState(str, Enum):
    ASSUMED = "ASSUMED"
    CALCULATED = "CALCULATED"
    SIMULATED = "SIMULATED"
    MEASURED = "MEASURED"
    CALIBRATED = "CALIBRATED"
    VALIDATED = "VALIDATED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Provenance:
    """Traceability metadata for an engineering observation."""

    source: str
    source_id: str
    model_revision: Optional[str] = None
    instrument_id: Optional[str] = None
    calibration_id: Optional[str] = None
    timestamp: Optional[str] = None


@dataclass(frozen=True)
class Observation:
    """A value tied to one physical variable and one building location."""

    building_name: str
    level_id: str
    room_id: str
    variable: str
    value: float
    unit: str
    state: EvidenceState
    provenance: Provenance
    uncertainty: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.building_name or not self.level_id or not self.room_id:
            raise ValueError("observation requires building, level, and room identity")
        if not self.variable or not self.unit:
            raise ValueError("observation requires variable and unit")
        if self.uncertainty is not None and self.uncertainty < 0:
            raise ValueError("uncertainty cannot be negative")
        if self.state is EvidenceState.MEASURED:
            if self.uncertainty is None:
                raise ValueError("measured observations require uncertainty")
            if not self.provenance.instrument_id:
                raise ValueError("measured observations require instrument provenance")
            if not self.provenance.calibration_id:
                raise ValueError("measured observations require calibration provenance")


@dataclass(frozen=True)
class Comparison:
    predicted: Observation
    measured: Optional[Observation]
    residual: Optional[float]
    combined_uncertainty: Optional[float]
    status: EvidenceState

    @classmethod
    def compare(
        cls, predicted: Observation, measured: Optional[Observation]
    ) -> "Comparison":
        if measured is None:
            return cls(
                predicted=predicted,
                measured=None,
                residual=None,
                combined_uncertainty=None,
                status=EvidenceState.UNKNOWN,
            )
        if predicted.level_id != measured.level_id or predicted.room_id != measured.room_id:
            raise ValueError("predicted and measured observations must share location")
        if predicted.variable != measured.variable or predicted.unit != measured.unit:
            raise ValueError("predicted and measured observations must share variable and unit")
        if measured.state is not EvidenceState.MEASURED:
            raise ValueError("comparison evidence must be an actual MEASURED observation")
        residual = measured.value - predicted.value
        combined = sqrt(
            (predicted.uncertainty or 0.0) ** 2 + (measured.uncertainty or 0.0) ** 2
        )
        return cls(
            predicted=predicted,
            measured=measured,
            residual=residual,
            combined_uncertainty=combined,
            status=EvidenceState.MEASURED,
        )

    def validate(self, tolerance: float) -> EvidenceState:
        """Return VALIDATED only when real measurement evidence meets tolerance."""
        if tolerance < 0:
            raise ValueError("validation tolerance cannot be negative")
        if self.measured is None or self.residual is None:
            return EvidenceState.UNKNOWN
        if self.measured.state is not EvidenceState.MEASURED:
            return EvidenceState.UNKNOWN
        if abs(self.residual) <= tolerance:
            return EvidenceState.VALIDATED
        return EvidenceState.MEASURED


@dataclass(frozen=True)
class BuildingPerformanceState:
    """A provenance-aware bridge between one BuildingModel and observations."""

    building_model: BuildingModel

    def observation(
        self,
        *,
        level_id: str,
        room_id: str,
        variable: str,
        value: float,
        unit: str,
        state: EvidenceState,
        provenance: Provenance,
        uncertainty: Optional[float] = None,
    ) -> Observation:
        if level_id not in self.building_model.levels:
            raise ValueError(f"unknown level: {level_id}")
        if room_id not in self.building_model.levels[level_id].rooms:
            raise ValueError(f"unknown room: {room_id}")
        return Observation(
            building_name=self.building_model.name,
            level_id=level_id,
            room_id=room_id,
            variable=variable,
            value=value,
            unit=unit,
            state=state,
            provenance=provenance,
            uncertainty=uncertainty,
        )
