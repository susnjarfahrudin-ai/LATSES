"""Building orientation and cardinal-direction reference frame."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CardinalDirection(str, Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


class ViewStyle(str, Enum):
    """User-facing representation modes for section and 3-D views."""

    CONSTRUCTIONAL_LINE = "constructional_line"
    NATURAL = "natural"


@dataclass(frozen=True)
class BuildingOrientation:
    """Reference orientation of the building footprint relative to north."""

    north_azimuth_deg: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.north_azimuth_deg < 360.0:
            raise ValueError("north_azimuth_deg must be between 0 and 360 degrees")

    @property
    def south_azimuth_deg(self) -> float:
        return (self.north_azimuth_deg + 180.0) % 360.0

    @property
    def east_azimuth_deg(self) -> float:
        return (self.north_azimuth_deg + 90.0) % 360.0

    @property
    def west_azimuth_deg(self) -> float:
        return (self.north_azimuth_deg + 270.0) % 360.0

    def direction_for_azimuth(self, azimuth_deg: float) -> CardinalDirection:
        relative = (azimuth_deg - self.north_azimuth_deg) % 360.0
        if relative < 45.0 or relative >= 315.0:
            return CardinalDirection.NORTH
        if relative < 135.0:
            return CardinalDirection.EAST
        if relative < 225.0:
            return CardinalDirection.SOUTH
        return CardinalDirection.WEST
