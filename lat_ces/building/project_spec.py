"""User-facing project specification collected before scientific solvers."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict

from .environment import SiteEnvironment
from .orientation import BuildingOrientation


@dataclass
class WallConstructionSpec:
    block_brand: str = ""
    block_length_m: float = 0.0
    block_width_m: float = 0.0
    block_height_m: float = 0.0
    wall_thickness_m: float = 0.0
    insulation_type: str = ""
    insulation_thickness_m: float = 0.0
    facade_brand: str = ""
    facade_granulation_mm: float = 0.0
    render_thickness_m: float = 0.0
    interior_cladding: str = ""
    exterior_cladding: str = ""


@dataclass
class JoinerySpec:
    material: str = ""
    glazing: str = ""
    frame_type: str = ""
    thermal_transmittance_w_m2k: float = 0.0
    opening_count: int = 0


@dataclass
class RoofSpec:
    roof_type: str = "Nije definisan"
    construction: str = ""
    covering: str = ""
    substructure: str = ""
    support: str = ""
    length_m: float = 0.0
    width_m: float = 0.0
    slope_deg: float = 0.0
    height_m: float = 0.0

    def __post_init__(self) -> None:
        if not self.roof_type.strip():
            raise ValueError("RoofSpec.roof_type must not be empty")
        if self.length_m < 0 or self.width_m < 0 or self.height_m < 0:
            raise ValueError("Roof dimensions must be >= 0")
        if not 0.0 <= self.slope_deg < 90.0:
            raise ValueError("Roof slope must be between 0 and 90 degrees")


@dataclass
class RoomSpec:
    name: str
    length_m: float = 0.0
    width_m: float = 0.0
    x_m: float = 0.0
    y_m: float = 0.0
    role: str = "room"

    @property
    def area_m2(self) -> float:
        return self.length_m * self.width_m


@dataclass
class LevelProjectSpec:
    name: str
    height_m: float = 2.80
    length_m: float = 0.0
    width_m: float = 0.0
    construction: WallConstructionSpec = field(default_factory=WallConstructionSpec)
    cladding: str = ""
    joinery: JoinerySpec = field(default_factory=JoinerySpec)
    rooms: list[RoomSpec] = field(default_factory=list)
    finalized: bool = False

    @property
    def room_count(self) -> int:
        return len(self.rooms)


@dataclass
class BuildingProjectSpec:
    name: str = "Novi objekat"
    floor_count: int = 0
    levels: list[LevelProjectSpec] = field(default_factory=list)
    floor_count_finalized: bool = False
    roof_shape: str = "Nije definisan"
    roof_height_m: float = 0.0
    roof: RoofSpec = field(default_factory=RoofSpec)
    orientation: BuildingOrientation = field(default_factory=BuildingOrientation)
    site: SiteEnvironment | None = None

    def set_floor_count(self, count: int) -> None:
        if count < 1 or count > 50:
            raise ValueError("Broj etaža mora biti između 1 i 50")
        self.floor_count = count
        self.floor_count_finalized = False
        while len(self.levels) < count:
            self.levels.append(LevelProjectSpec(name=f"Etaža {len(self.levels) + 1}"))
        if len(self.levels) > count:
            self.levels = self.levels[:count]

    def set_site(self, site: SiteEnvironment) -> None:
        if not (-90.0 <= site.latitude_deg <= 90.0):
            raise ValueError("Geografska širina mora biti između -90 i 90 stepeni")
        if not (-180.0 <= site.longitude_deg <= 180.0):
            raise ValueError("Geografska dužina mora biti između -180 i 180 stepeni")
        self.site = site

    def set_orientation(self, north_azimuth_deg: float) -> None:
        self.orientation = BuildingOrientation(north_azimuth_deg=north_azimuth_deg)

    def all_levels_finalized(self) -> bool:
        return self.floor_count > 0 and len(self.levels) == self.floor_count and all(
            level.finalized for level in self.levels
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
