"""View contract for the canonical 3-D building representation."""
from __future__ import annotations

from dataclasses import dataclass

from .geometry3d import LevelGeometry3D
from .orientation import ViewStyle


@dataclass(frozen=True)
class Model3DView:
    """Two presentation modes over the same canonical 3-D geometry."""

    levels: tuple[LevelGeometry3D, ...]
    style: ViewStyle = ViewStyle.CONSTRUCTIONAL_LINE
    show_materials: bool = False
    show_openings: bool = True

    @property
    def is_line_based(self) -> bool:
        return self.style is ViewStyle.CONSTRUCTIONAL_LINE

    @property
    def is_natural(self) -> bool:
        return self.style is ViewStyle.NATURAL
