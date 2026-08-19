"""Small two-storey reference house used as an integration model for LATCES.

The example is intentionally deterministic: two 10 x 8 m levels,
2.80 m storey height, four rooms per level, real walls/openings, and
material data. It is a seed model for connecting one geometry to downstream
engineering while exercising multi-level volume aggregation.
"""
from .core import BuildingModel, Level, Material, Opening, Room, Wall


def _id(base: str, level: Level) -> str:
    return base if level.id == "L0" else f"{base}-{level.id}"


def _populate_reference_level(level: Level, brick: Material, concrete: Material, *, room_offset: int = 0) -> None:
    level.add_room(Room(f"R{room_offset + 1}", "Living" if room_offset == 0 else "Living Upper", 5.0, 4.0, 2.80))
    level.add_room(Room(f"R{room_offset + 2}", "Kitchen" if room_offset == 0 else "Kitchen Upper", 5.0, 4.0, 2.80))
    level.add_room(Room(f"R{room_offset + 3}", "Bedroom" if room_offset == 0 else "Bedroom Upper", 5.0, 4.0, 2.80))
    level.add_room(Room(f"R{room_offset + 4}", "Service" if room_offset == 0 else "Service Upper", 5.0, 4.0, 2.80))

    # Exterior walls: 20 cm brick, 2.80 m high.
    south = Wall(_id("W-S", level), 10.0, 0.20, 2.80, brick)
    south.add_opening(Opening("door", 0.90, 2.10, position_m=1.20))
    south.add_opening(Opening("window", 1.50, 1.20, sill_height_m=0.90, position_m=5.00))
    north = Wall(_id("W-N", level), 10.0, 0.20, 2.80, brick)
    north.add_opening(Opening("window", 1.50, 1.20, sill_height_m=0.90, position_m=3.00))
    east = Wall(_id("W-E", level), 8.0, 0.20, 2.80, brick)
    west = Wall(_id("W-W", level), 8.0, 0.20, 2.80, brick)

    # One representative structural partition.
    partition = Wall(_id("W-P1", level), 8.0, 0.10, 2.80, concrete)
    partition.add_opening(Opening("door", 0.80, 2.10, position_m=3.50))

    for wall in (south, north, east, west, partition):
        level.add_wall(wall)


def make_small_reference_house() -> BuildingModel:
    """Return a compact, fully populated two-level BuildingModel reference case."""
    brick = Material("brick", density_kg_m3=1800.0, conductivity_w_mk=0.72)
    concrete = Material("reinforced concrete", density_kg_m3=2400.0, conductivity_w_mk=2.30)
    building = BuildingModel(name="LATCES Small Reference House")
    building.materials[brick.name] = brick
    building.materials[concrete.name] = concrete

    ground = Level("L0", "Ground floor", 10.0, 8.0, 2.80)
    _populate_reference_level(ground, brick, concrete, room_offset=0)
    building.add_level(ground)

    upper = Level("L1", "Upper floor", 10.0, 8.0, 2.80)
    _populate_reference_level(upper, brick, concrete, room_offset=4)
    building.add_level(upper)

    return building
