"""Authoritative, GUI-independent building geometry and construction model."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass(frozen=True)
class Material:
    name: str
    density_kg_m3: Optional[float] = None
    conductivity_w_mk: Optional[float] = None
    compressive_strength_mpa: Optional[float] = None
    product_id: Optional[str] = None
    manufacturer: Optional[str] = None


@dataclass
class Opening:
    kind: str
    width_m: float
    height_m: float
    sill_height_m: float = 0.0
    position_m: float = 0.0

    def __post_init__(self):
        if self.kind not in {"door", "window"}:
            raise ValueError("opening kind must be 'door' or 'window'")
        if self.width_m <= 0 or self.height_m <= 0 or self.sill_height_m < 0:
            raise ValueError("opening dimensions must be positive")

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
    exterior: bool = False
    load_bearing: bool = False

    @property
    def partition(self) -> bool:
        return not self.load_bearing

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
        if not self.openings:
            return [(0.0, self.height_m)]
        result, cursor = [], 0.0
        for opening in sorted(self.openings, key=lambda o: o.z_bottom_m):
            if opening.z_bottom_m > cursor:
                result.append((cursor, opening.z_bottom_m))
            cursor = max(cursor, opening.z_top_m)
        if cursor < self.height_m:
            result.append((cursor, self.height_m))
        return result


@dataclass
class Stair:
    id: str
    length_m: float
    width_m: float
    riser_count: Optional[int] = None
    riser_height_m: Optional[float] = None
    tread_width_m: Optional[float] = None
    landing: bool = False
    railing: bool = False
    floor_opening: bool = False


@dataclass
class Terrace:
    id: str
    length_m: float
    width_m: float
    construction_type: str = "concrete"
    material: Optional[Material] = None


@dataclass
class Ceiling:
    suspended: bool = False
    clear_height_m: Optional[float] = None


@dataclass
class Room:
    id: str
    name: str
    length_m: float
    width_m: float
    height_m: Optional[float] = None
    ceiling: Ceiling = field(default_factory=Ceiling)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("room name cannot be empty")
        if self.length_m <= 0 or self.width_m <= 0:
            raise ValueError("room dimensions must be positive")
        if self.height_m is not None and self.height_m <= 0:
            raise ValueError("room height must be positive")

    def resolve_height(self, level_height_m: float) -> float:
        if level_height_m <= 0:
            raise ValueError("level height must be positive")
        if self.ceiling.suspended:
            if self.ceiling.clear_height_m is None or self.ceiling.clear_height_m <= 0:
                raise ValueError("suspended ceiling requires clear height")
            return self.ceiling.clear_height_m
        return self.height_m if self.height_m is not None else level_height_m

    @property
    def floor_area_m2(self) -> float:
        return self.length_m * self.width_m

    @property
    def volume_m3(self) -> float:
        if self.height_m is None:
            raise ValueError("room height must be resolved from its level before volume calculation")
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
    stairs: Dict[str, Stair] = field(default_factory=dict)
    terraces: Dict[str, Terrace] = field(default_factory=dict)

    def add_room(self, room: Room) -> None:
        if room.id in self.rooms:
            raise ValueError(f"duplicate room id: {room.id}")
        if room.height_m is None:
            room.height_m = room.resolve_height(self.height_m)
        self.rooms[room.id] = room

    def add_wall(self, wall: Wall) -> None:
        if wall.id in self.walls:
            raise ValueError(f"duplicate wall id: {wall.id}")
        self.walls[wall.id] = wall

    def add_stair(self, stair: Stair) -> None:
        if stair.id in self.stairs:
            raise ValueError(f"duplicate stair id: {stair.id}")
        self.stairs[stair.id] = stair

    def add_terrace(self, terrace: Terrace) -> None:
        if terrace.id in self.terraces:
            raise ValueError(f"duplicate terrace id: {terrace.id}")
        self.terraces[terrace.id] = terrace


@dataclass
class BuildingModel:
    building_model_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Untitled"
    levels: Dict[str, Level] = field(default_factory=dict)
    materials: Dict[str, Material] = field(default_factory=dict)
    load_bearing_mode: str = "all_walls"

    def __post_init__(self):
        if not self.building_model_id.strip():
            raise ValueError("building_model_id cannot be empty")
        if self.load_bearing_mode not in {"all_walls", "exterior_only"}:
            raise ValueError("load_bearing_mode must be 'all_walls' or 'exterior_only'")

    def add_level(self, level: Level) -> None:
        if level.id in self.levels:
            raise ValueError(f"duplicate level id: {level.id}")
        self.levels[level.id] = level

    def total_volume_m3(self) -> float:
        return sum(r.volume_m3 for l in self.levels.values() for r in l.rooms.values())
