"""Minimal authoritative spatial representation for BuildingModel."""
from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class WallPlacement:
    """Authoritative wall centerline endpoints in level-local coordinates."""

    x1_m: float
    y1_m: float
    x2_m: float
    y2_m: float

    @property
    def length_m(self) -> float:
        return hypot(self.x2_m - self.x1_m, self.y2_m - self.y1_m)

    def validate_length(self, declared_length_m: float, tolerance_m: float = 1e-9) -> None:
        if abs(self.length_m - declared_length_m) > tolerance_m:
            raise ValueError(
                "wall placement length disagrees with declared wall length"
            )
