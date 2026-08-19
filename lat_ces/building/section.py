"""Section view contract derived from the canonical BuildingModel."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .geometry3d import LevelGeometry3D
from .orientation import CardinalDirection, ViewStyle


class SectionAxis(str, Enum):
    X = "X"
    Y = "Y"


@dataclass(frozen=True)
class SectionDefinition:
    """A vertical cut through the shared model; no independent geometry source."""

    axis: SectionAxis = SectionAxis.X
    position_m: float = 0.0
    style: ViewStyle = ViewStyle.CONSTRUCTIONAL_LINE


@dataclass(frozen=True)
class SectionView:
    """Solver-neutral section description consumed by GUI renderers."""

    definition: SectionDefinition
    levels: tuple[LevelGeometry3D, ...]
    north_direction: CardinalDirection = CardinalDirection.NORTH

    @property
    def is_line_based(self) -> bool:
        return self.definition.style is ViewStyle.CONSTRUCTIONAL_LINE

    @property
    def is_natural(self) -> bool:
        return self.definition.style is ViewStyle.NATURAL
