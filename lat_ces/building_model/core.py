"""Authoritative, GUI-independent building geometry model.

All dimensions are SI metres. Geometry is deliberately simple in Phase 1,
but openings are real volumetric relationships rather than drawing symbols.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: Optional[float] = None
    conductivity_w_mk: Optional[float] = None


@dataclass
class Opening:
    kind: str  # door | window
    width_m: float
    height_m: float
    sill_height_m: float = 0.0
    position_m: float = 0.0

    def __post_init__(self):
        if self.kind not in {"door", "window"}:
            raise ValueError("opening kind must be 'door' or 'window'")
        if self.width_m <= 0 or self.height_m <= 0:
            raise ValueError("opening dimensions must be positive")
        if self.sill_height_m < 0:
            raise ValueError("sill height cannot be negative")

    @property
    def z_bottom_m(self) -> float:
        return self.sill_height_m

    @property
    def z_top_m(self) -> float:
        return self.sill_height_m + self.height_m


@dataclass
class Wall:
    id: str
    length_m: float
    thickness_m: float
    height_m: float
    material: Optional[Material] = None
    openings: List[Opening] = field(default_factory=list)

    def __post_init__(self):
        if min(self.length_m, self.thickness_m, self.height_m) <= 0:
            raise ValueError("wall dimensions must be positive")

    def add_opening(self, opening: Opening) -> None:
        if opening.position_m < 0 or opening.position_m + opening.width_m > self.length_m:
            raise ValueError("opening lies outside wall length")
        if opening.z_top_m > self.height_m:
            raise ValueError("opening lies above wall height")
        self.openings.append(opening)

    def solid_vertical_segments(self) -> List[tuple]:
        """Return wall solid z-segments for a single door/opening profile.

        For a door from z=0 to 2.10 m in a 2.80 m wall this returns
        [(2.10, 2.80)]. Multiple/complex openings are intentionally handled
        conservatively in Phase 1 and validated separately.
        """
        if not self.openings:
            return [(0.0, self.height_m)]
        result = []
        cursor = 0.0
        for opening in sorted(self.openings, key=lambda o: o.z_bottom_m):
            if opening.z_bottom_m > cursor:
                result.append((cursor, opening.z_bottom_m))
            cursor = max(cursor, opening.z_top_m)
        if cursor < self.height_m:
            result.append((cursor, self.height_m))
        return result


@dataclass
class Room:
    id: str
    name: str
    length_m: float
    width_m: float
    height_m: float

    @property
    def floor_area_m2(self) -> float:
        return self.length_m * self.width_m

    @property
    def volume_m3(self) -> float:
        return self.floor_area_m2 * self.height_m


@dataclass
class Level:
    id: str
    name: str
    length_m: float
    width_m: float
    height_m: float
    rooms: Dict[str, Room] = field(default_factory=dict)
    walls: Dict[str, Wall] = field(default_factory=dict)

    def add_room(self, room: Room) -> None:
        if room.id in self.rooms:
            raise ValueError(f"duplicate room id: {room.id}")
        self.rooms[room.id] = room

    def add_wall(self, wall: Wall) -> None:
        if wall.id in self.walls:
            raise ValueError(f"duplicate wall id: {wall.id}")
        self.walls[wall.id] = wall


@dataclass
class BuildingModel:
    name: str = "Untitled"
    levels: Dict[str, Level] = field(default_factory=dict)
    materials: Dict[str, Material] = field(default_factory=dict)

    def add_level(self, level: Level) -> None:
        if level.id in self.levels:
            raise ValueError(f"duplicate level id: {level.id}")
        self.levels[level.id] = level

    def total_volume_m3(self) -> float:
        return sum(r.volume_m3 for l in self.levels.values() for r in l.rooms.values())
