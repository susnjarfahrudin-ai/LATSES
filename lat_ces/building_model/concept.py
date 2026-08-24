"""Canonical BuildingModel concept contract for the next LAT-CES architecture.

This module is deliberately GUI-independent.  It describes the information
that the basic model owns and the information that downstream structural,
MEP and illustration models may consume.  It does not silently invent design
loads, manufacturer limits, code parameters, or measured conditions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple


class LevelKind(str, Enum):
    BASEMENT = "basement"
    GROUND = "ground"
    FLOOR = "floor"
    ATTIC = "attic"
    ROOF = "roof"
    FOUNDATION = "foundation"


class RoofShape(str, Enum):
    FLAT = "flat"
    MONOPITCH = "monopitch"
    GABLE = "gable"
    HIP = "hip"
    HIDDEN_MONOPITCH = "hidden_monopitch"
    DOME = "dome"
    COMPOSITE = "composite"


class RoofSupport(str, Enum):
    RC_SLAB = "reinforced_concrete_slab"
    MASONRY_RING_BEAM = "masonry_with_ring_beam"
    TIMBER = "timber"
    STEEL = "steel"
    CONCRETE_ELEMENTS = "concrete_elements"


class RoofStructure(str, Enum):
    TIMBER_BEAMS = "timber_beams"
    STEEL_PROFILES = "steel_profiles"
    CONCRETE_ELEMENTS = "concrete_elements"
    RC_SLOPED_SLAB = "reinforced_concrete_sloped_slab"


class RoofSubstructure(str, Enum):
    BATTENS = "battens"
    COUNTER_BATTENS_BATTENS = "counter_battens_and_battens"
    BOARDED_COUNTER_BATTENS_BATTENS = "boards_counter_battens_and_battens"


class RoofCover(str, Enum):
    TILE = "tile"
    SHEET_METAL = "sheet_metal"
    CONCRETE_TILE = "concrete_tile"
    SANDWICH_PANEL = "sandwich_panel"
    SHINGLE = "shingle"
    TIMBER = "timber"


class InsulationKind(str, Enum):
    NONE = "none"
    ROCK_WOOL = "rock_wool"
    GLASS_MINERAL_WOOL = "glass_mineral_wool"
    EPS = "eps"
    OTHER = "other"


class ConstructionKind(str, Enum):
    MASONRY = "masonry"
    CONCRETE = "concrete"
    TIMBER = "timber"
    STEEL = "steel"
    PREFAB_CONCRETE = "prefabricated_concrete"
    GYPSUM = "gypsum"


class WindowMaterial(str, Enum):
    PVC = "pvc"
    ALUMINIUM = "aluminium"
    TIMBER = "timber"


class MEPSystem(str, Enum):
    WATER = "water"
    DRAINAGE = "drainage"
    ELECTRICAL = "electrical"
    HEATING = "heating"
    COOLING = "cooling"
    VENTILATION = "ventilation"
    ACOUSTICS = "acoustics"


@dataclass(frozen=True)
class RoofCoverSpec:
    cover: RoofCover
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    recommended_pitch_deg: Optional[float] = None
    minimum_pitch_deg: Optional[float] = None
    mass_kg_m2: Optional[float] = None
    provenance: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.recommended_pitch_deg is not None and not 0 <= self.recommended_pitch_deg < 90:
            raise ValueError("recommended roof pitch must be in [0, 90) degrees")
        if self.minimum_pitch_deg is not None and not 0 <= self.minimum_pitch_deg < 90:
            raise ValueError("minimum roof pitch must be in [0, 90) degrees")
        if self.mass_kg_m2 is not None and self.mass_kg_m2 < 0:
            raise ValueError("roof-cover mass cannot be negative")
        if self.recommended_pitch_deg is not None and self.minimum_pitch_deg is not None:
            if self.recommended_pitch_deg < self.minimum_pitch_deg:
                raise ValueError("recommended pitch cannot be below minimum pitch")


@dataclass(frozen=True)
class RoofModel:
    length_m: float
    width_m: float
    shape: RoofShape
    support: RoofSupport
    structure: RoofStructure
    substructure: RoofSubstructure
    cover: RoofCoverSpec
    insulation_kind: InsulationKind = InsulationKind.NONE
    insulation_thickness_m: float = 0.0
    finish: Optional[str] = None
    pitch_deg: Optional[float] = None
    orientation_deg: Optional[float] = None
    overhang_m: float = 0.0
    provenance: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.length_m <= 0 or self.width_m <= 0:
            raise ValueError("roof plan dimensions must be positive")
        if self.insulation_thickness_m < 0 or self.overhang_m < 0:
            raise ValueError("roof insulation and overhang cannot be negative")
        if self.pitch_deg is not None and not 0 <= self.pitch_deg < 90:
            raise ValueError("roof pitch must be in [0, 90) degrees")
        if self.orientation_deg is not None and not 0 <= self.orientation_deg < 360:
            raise ValueError("roof orientation must be in [0, 360) degrees")

    @property
    def plan_area_m2(self) -> float:
        return self.length_m * self.width_m

    def effective_pitch_deg(self) -> Optional[float]:
        """Return explicit pitch, otherwise the catalog recommendation.

        A recommendation is not an approval: structural verification remains
        a downstream responsibility and must retain the catalog provenance.
        """
        return self.pitch_deg if self.pitch_deg is not None else self.cover.recommended_pitch_deg


@dataclass(frozen=True)
class MaterialSelection:
    category: str
    material: str
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    thickness_m: Optional[float] = None
    density_kg_m3: Optional[float] = None
    provenance: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.thickness_m is not None and self.thickness_m < 0:
            raise ValueError("material thickness cannot be negative")
        if self.density_kg_m3 is not None and self.density_kg_m3 < 0:
            raise ValueError("material density cannot be negative")


@dataclass(frozen=True)
class OpeningSpec:
    id: str
    kind: str
    width_m: float
    height_m: float
    sill_height_m: float = 0.0
    material: Optional[WindowMaterial] = None
    orientation_deg: Optional[float] = None

    def __post_init__(self) -> None:
        if self.kind not in {"door", "window"}:
            raise ValueError("opening kind must be door or window")
        if self.width_m <= 0 or self.height_m <= 0:
            raise ValueError("opening dimensions must be positive")
        if self.sill_height_m < 0:
            raise ValueError("sill height cannot be negative")


@dataclass(frozen=True)
class SystemNode:
    id: str
    system: MEPSystem
    name: str
    level_id: str
    room_id: Optional[str] = None
    x_m: Optional[float] = None
    y_m: Optional[float] = None
    z_m: Optional[float] = None


@dataclass(frozen=True)
class StructuralLoadInput:
    snow_kN_m2: Optional[float] = None
    rain_kN_m2: Optional[float] = None
    wind_kN_m2: Optional[float] = None
    imposed_kN_m2: Optional[float] = None
    seismic_class: Optional[str] = None
    standard_reference: Optional[str] = None
    provenance: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in ("snow_kN_m2", "rain_kN_m2", "wind_kN_m2", "imposed_kN_m2"):
            value = getattr(self, name)
            if value is not None and value < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass
class BuildingConcept:
    """The handoff object shared by Basic, Structural and MEP models."""

    name: str
    levels: Dict[str, LevelKind] = field(default_factory=dict)
    level_dimensions: Dict[str, Tuple[float, float, float]] = field(default_factory=dict)
    rooms: Dict[str, Tuple[str, float, float]] = field(default_factory=dict)
    openings: Dict[str, OpeningSpec] = field(default_factory=dict)
    materials: Dict[str, MaterialSelection] = field(default_factory=dict)
    roof: Optional[RoofModel] = None
    system_nodes: Dict[str, SystemNode] = field(default_factory=dict)
    structural_loads: Optional[StructuralLoadInput] = None

    def add_level(self, level_id: str, kind: LevelKind, length_m: float, width_m: float, height_m: float) -> None:
        if level_id in self.levels:
            raise ValueError(f"duplicate level id: {level_id}")
        if min(length_m, width_m, height_m) <= 0:
            raise ValueError("level dimensions must be positive")
        self.levels[level_id] = kind
        self.level_dimensions[level_id] = (length_m, width_m, height_m)

    def add_room(self, room_id: str, level_id: str, length_m: float, width_m: float) -> None:
        if level_id not in self.levels:
            raise ValueError(f"unknown level: {level_id}")
        if room_id in self.rooms:
            raise ValueError(f"duplicate room id: {room_id}")
        if min(length_m, width_m) <= 0:
            raise ValueError("room dimensions must be positive")
        self.rooms[room_id] = (level_id, length_m, width_m)

    def add_system_node(self, node: SystemNode) -> None:
        if node.id in self.system_nodes:
            raise ValueError(f"duplicate system node id: {node.id}")
        if node.level_id not in self.levels:
            raise ValueError(f"unknown level: {node.level_id}")
        if node.room_id is not None and node.room_id not in self.rooms:
            raise ValueError(f"unknown room: {node.room_id}")
        self.system_nodes[node.id] = node

    def level_volume_m3(self, level_id: str) -> float:
        length, width, height = self.level_dimensions[level_id]
        return length * width * height

    def total_volume_m3(self) -> float:
        return sum(self.level_volume_m3(level_id) for level_id in self.levels)

    def nodes_for(self, system: MEPSystem) -> Tuple[SystemNode, ...]:
        return tuple(node for node in self.system_nodes.values() if node.system == system)
