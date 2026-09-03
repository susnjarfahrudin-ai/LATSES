"""Canonical 2-D floor-plan primitives for the BuildingModel.

The floor plan is solver-neutral topology and geometry. Scientific modules
consume these same wall/opening objects; they do not define copies.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import hypot
from uuid import uuid4


@dataclass(frozen=True)
class Point2D:
    x: float
    y: float


@dataclass(frozen=True)
class Segment2D:
    start: Point2D
    end: Point2D

    @property
    def length(self) -> float:
        return hypot(self.end.x - self.start.x, self.end.y - self.start.y)


@dataclass(frozen=True)
class Opening:
    """Opening in a wall: door, window, service opening, etc."""

    kind: str
    offset: float
    width: float
    height_m: float = 2.10
    opening_id: str = field(default_factory=lambda: f"OPN-{uuid4()}")

    def __post_init__(self) -> None:
        if not self.kind.strip():
            raise ValueError("Opening.kind must not be empty")
        if self.offset < 0 or self.width <= 0:
            raise ValueError("Opening offset must be >= 0 and width must be > 0")
        if self.height_m <= 0:
            raise ValueError("Opening.height_m must be > 0")


@dataclass
class Wall:
    """Canonical wall object shared by GUI and scientific consumers."""

    name: str
    segment: Segment2D
    thickness: float = 0.2
    wall_id: str = field(default_factory=lambda: f"WALL-{uuid4()}")
    openings: list[Opening] = field(default_factory=list)
    load_bearing: bool = False
    material_id: str | None = None
    tributary_width_m: float = 0.0
    exterior: bool = False
    room_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Wall.name must not be empty")
        if self.segment.length <= 0:
            raise ValueError("Wall segment must have non-zero length")
        if self.thickness <= 0:
            raise ValueError("Wall.thickness must be > 0")
        if self.tributary_width_m < 0:
            raise ValueError("Wall.tributary_width_m must be >= 0")

    def add_opening(self, opening: Opening) -> Opening:
        if opening.offset + opening.width > self.segment.length:
            raise ValueError("Opening extends beyond wall segment")
        if any(
            opening.offset < existing.offset + existing.width
            and existing.offset < opening.offset + opening.width
            for existing in self.openings
        ):
            raise ValueError("Opening overlaps an existing opening")
        self.openings.append(opening)
        return opening

    @property
    def net_length(self) -> float:
        return self.segment.length - sum(opening.width for opening in self.openings)

    @property
    def role_label(self) -> str:
        return "Nosivi zid" if self.load_bearing else "Pregradni / nenosivi zid"


@dataclass
class FloorPlan:
    """2-D geometric/topological representation associated with one level."""

    name: str
    walls: dict[str, Wall] = field(default_factory=dict)
    plan_id: str = field(default_factory=lambda: f"PLAN-{uuid4()}")

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("FloorPlan.name must not be empty")

    def add_wall(self, wall: Wall) -> Wall:
        if wall.wall_id in self.walls:
            raise ValueError(f"Duplicate wall id: {wall.wall_id}")
        self.walls[wall.wall_id] = wall
        return wall

    @property
    def wall_count(self) -> int:
        return len(self.walls)

    @property
    def load_bearing_wall_count(self) -> int:
        return sum(wall.load_bearing for wall in self.walls.values())

    @property
    def gross_wall_length(self) -> float:
        return sum(wall.segment.length for wall in self.walls.values())

    @property
    def net_wall_length(self) -> float:
        return sum(wall.net_length for wall in self.walls.values())

    def validate(self) -> list[str]:
        findings: list[str] = []
        for wall in self.walls.values():
            for opening in wall.openings:
                if opening.offset + opening.width > wall.segment.length:
                    findings.append(
                        f"Opening {opening.opening_id} exceeds wall {wall.wall_id}"
                    )
            if wall.load_bearing and wall.tributary_width_m <= 0.0:
                findings.append(f"Load-bearing wall {wall.wall_id} has no tributary width")
            if len(set(wall.room_ids)) != len(wall.room_ids):
                findings.append(f"Wall {wall.wall_id} has duplicate room identity")
        return findings
