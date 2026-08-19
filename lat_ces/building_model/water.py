"""Water engineering and microbiological-quality evidence model."""
from dataclasses import dataclass
from enum import Enum


class WaterQualityStatus(str, Enum):
    UNKNOWN = "UNKNOWN"
    ACCEPTABLE = "ACCEPTABLE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class WaterResult:
    flow_m3_s: float
    velocity_m_s: float
    pressure_drop_pa: float


def calculate_water_flow(flow_m3_s: float, diameter_m: float, pressure_drop_pa: float = 0.0) -> WaterResult:
    if flow_m3_s < 0 or diameter_m <= 0 or pressure_drop_pa < 0:
        raise ValueError("invalid water input")
    area = 3.141592653589793 * diameter_m ** 2 / 4.0
    return WaterResult(flow_m3_s, flow_m3_s / area, pressure_drop_pa)


@dataclass(frozen=True)
class WaterQualityEvidence:
    status: WaterQualityStatus
    source: str
    measured: bool = False
    note: str = ""

    @property
    def confidence_class(self) -> str:
        if self.measured:
            return "MEASURED"
        if self.source:
            return "DECLARED_OR_RESEARCHED"
        return "UNKNOWN"
