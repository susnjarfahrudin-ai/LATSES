"""Deterministic Reference House fixture for Building Model validation.

The fixture intentionally uses the public model API only. It is a validation
fixture, not a GUI or scientific-engine replacement.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json


@dataclass(frozen=True)
class Product:
    product_id: str
    category: str
    manufacturer: str
    name: str
    dimensions_m: tuple[float, float, float]
    thermal_conductivity_w_mk: float
    density_kg_m3: float
    compressive_strength_mpa: float


@dataclass(frozen=True)
class Wall:
    wall_id: str
    room_a: str
    room_b: str | None
    exterior: bool
    load_bearing: bool
    thickness_m: float
    product_id: str
    openings: tuple[str, ...] = ()


@dataclass(frozen=True)
class Room:
    room_id: str
    name: str
    length_m: float
    width_m: float
    clear_height_m: float


@dataclass(frozen=True)
class Opening:
    opening_id: str
    wall_id: str
    kind: str
    width_m: float
    height_m: float
    target_room_id: str | None = None


@dataclass(frozen=True)
class Stair:
    stair_id: str
    risers: int
    riser_height_m: float
    tread_width_m: float
    landing: bool
    railing: bool
    slab_opening_m2: float


@dataclass(frozen=True)
class Terrace:
    terrace_id: str
    length_m: float
    width_m: float
    structure: str
    product_id: str


@dataclass(frozen=True)
class ReferenceHouse:
    name: str
    storey_height_m: float
    rooms: tuple[Room, ...]
    products: tuple[Product, ...]
    walls: tuple[Wall, ...]
    openings: tuple[Opening, ...]
    stairs: tuple[Stair, ...]
    terraces: tuple[Terrace, ...]
    load_bearing_mode: str

    def validate(self) -> None:
        if self.load_bearing_mode not in {"all_walls", "exterior_only"}:
            raise ValueError("invalid load-bearing mode")
        if self.storey_height_m <= 0:
            raise ValueError("storey height must be positive")

        rooms = {room.room_id: room for room in self.rooms}
        products = {product.product_id: product for product in self.products}
        walls = {wall.wall_id: wall for wall in self.walls}
        openings = {opening.opening_id: opening for opening in self.openings}

        if len(rooms) != len(self.rooms) or len(products) != len(self.products):
            raise ValueError("duplicate room or product identity")
        if len(walls) != len(self.walls) or len(openings) != len(self.openings):
            raise ValueError("duplicate wall or opening identity")

        for room in self.rooms:
            if min(room.length_m, room.width_m, room.clear_height_m) <= 0:
                raise ValueError(f"invalid dimensions for room {room.room_id}")
            if room.clear_height_m > self.storey_height_m:
                raise ValueError(f"room exceeds storey height: {room.room_id}")

        for wall in self.walls:
            if wall.room_a not in rooms:
                raise ValueError(f"unknown room_a: {wall.room_id}")
            if wall.room_b is not None and wall.room_b not in rooms:
                raise ValueError(f"unknown room_b: {wall.wall_id}")
            if wall.product_id not in products:
                raise ValueError(f"unknown wall product: {wall.wall_id}")
            expected = wall.exterior if self.load_bearing_mode == "exterior_only" else True
            if wall.load_bearing != expected:
                raise ValueError(f"load-bearing policy mismatch: {wall.wall_id}")

        for opening in self.openings:
            if opening.wall_id not in walls:
                raise ValueError(f"opening references unknown wall: {opening.opening_id}")
            if opening.target_room_id is not None and opening.target_room_id not in rooms:
                raise ValueError(f"opening target unknown: {opening.opening_id}")
            if min(opening.width_m, opening.height_m) <= 0:
                raise ValueError(f"invalid opening dimensions: {opening.opening_id}")

        for stair in self.stairs:
            if stair.risers <= 0 or min(stair.riser_height_m, stair.tread_width_m) <= 0:
                raise ValueError(f"invalid stair geometry: {stair.stair_id}")
            if stair.slab_opening_m2 <= 0:
                raise ValueError(f"invalid stair opening: {stair.stair_id}")

        for terrace in self.terraces:
            if min(terrace.length_m, terrace.width_m) <= 0:
                raise ValueError(f"invalid terrace geometry: {terrace.terrace_id}")
            if terrace.product_id not in products:
                raise ValueError(f"unknown terrace product: {terrace.terrace_id}")

    def to_dict(self) -> dict:
        """Return a deterministic, JSON-safe representation."""
        return asdict(self)

    def serialize(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


THERMO_BLOCK = Product(
    "masonry:example:thermoblock-25", "masonry_block", "Example Manufacturer",
    "Thermo Block 25", (0.25, 0.25, 0.30), 0.18, 800.0, 10.0,
)
CONCRETE = Product(
    "concrete:example:c25-30", "concrete", "Example Manufacturer",
    "Concrete C25/30", (0.20, 0.20, 0.20), 1.70, 2400.0, 25.0,
)


def build_reference_house() -> ReferenceHouse:
    rooms = (
        Room("room-hall", "Hodnik", 4.0, 2.0, 2.70),
        Room("room-kitchen", "Kuhinja", 3.5, 3.0, 2.70),
        Room("room-living", "Dnevni boravak", 5.0, 4.0, 2.70),
        Room("room-bed1", "Soba 1", 3.5, 3.5, 2.70),
        Room("room-bed2", "Soba 2", 3.5, 3.0, 2.70),
    )
    walls = (
        Wall("wall-ext-n", "room-hall", None, True, True, 0.25, THERMO_BLOCK.product_id),
        Wall("wall-ext-s", "room-living", None, True, True, 0.25, THERMO_BLOCK.product_id),
        Wall("wall-ext-e", "room-kitchen", None, True, True, 0.25, THERMO_BLOCK.product_id),
        Wall("wall-ext-w", "room-bed1", None, True, True, 0.25, THERMO_BLOCK.product_id),
        Wall("wall-hall-kitchen", "room-hall", "room-kitchen", False, False, 0.12, THERMO_BLOCK.product_id, ("door-hall-kitchen",)),
        Wall("wall-hall-living", "room-hall", "room-living", False, False, 0.12, THERMO_BLOCK.product_id, ("door-hall-living",)),
        Wall("wall-hall-bed1", "room-hall", "room-bed1", False, False, 0.12, THERMO_BLOCK.product_id, ("door-hall-bed1",)),
        Wall("wall-hall-bed2", "room-hall", "room-bed2", False, False, 0.12, THERMO_BLOCK.product_id, ("door-hall-bed2",)),
    )
    openings = (
        Opening("door-hall-kitchen", "wall-hall-kitchen", "door", 0.90, 2.10, "room-kitchen"),
        Opening("door-hall-living", "wall-hall-living", "door", 0.90, 2.10, "room-living"),
        Opening("door-hall-bed1", "wall-hall-bed1", "door", 0.80, 2.10, "room-bed1"),
        Opening("door-hall-bed2", "wall-hall-bed2", "door", 0.80, 2.10, "room-bed2"),
        Opening("window-kitchen", "wall-ext-e", "window", 1.20, 1.20, None),
        Opening("window-living", "wall-ext-s", "window", 1.80, 1.40, None),
    )
    return ReferenceHouse(
        "Reference House",
        2.70,
        rooms,
        (THERMO_BLOCK, CONCRETE),
        walls,
        openings,
        (Stair("stair-main", 16, 0.16875, 0.28, True, True, 3.20),),
        (Terrace("terrace-main", 5.0, 2.5, "reinforced_concrete", CONCRETE.product_id),),
        "exterior_only",
    )


if __name__ == "__main__":
    house = build_reference_house()
    house.validate()
    print(house.serialize())
