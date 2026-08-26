from lat_ces.building.mep_zones import UnderfloorZone


def test_underfloor_zone_modes_support_full_and_two_halves():
    full = UnderfloorZone("z-full", "ufh-1", "room-1", "level-1", mode="full")
    half_a = UnderfloorZone("z-a", "ufh-1", "room-1", "level-1", mode="half_a")
    half_b = UnderfloorZone("z-b", "ufh-1", "room-1", "level-1", mode="half_b")

    assert full.zone_count == 1
    assert half_a.zone_count == 2
    assert half_b.zone_count == 2
    assert half_a.zone_index == 0
    assert half_b.zone_index == 1
    assert half_a.label == "1/2 — A"
    assert half_b.label == "1/2 — B"
