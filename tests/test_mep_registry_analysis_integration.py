from lat_ces.building_model.integration import analyze_building
from lat_ces.building_model.core import BuildingModel, Level, Room
from lat_ces.building.mep import HeatingZone, ensure_mep_registry


def _model_with_room():
    model = BuildingModel(name="MEP integration")
    level = Level(
        id="level-1",
        name="Ground",
        length_m=10.0,
        width_m=10.0,
        height_m=2.8,
    )
    level.add_room(
        Room(
            id="room-1",
            name="Living",
            length_m=5.0,
            width_m=4.0,
            height_m=2.8,
        )
    )
    model.add_level(level)
    return model


def _zone(room_id, zone_id, emitter_type):
    return HeatingZone(
        id=zone_id,
        room_id=room_id,
        emitter_type=emitter_type,
        design_supply_temp_c=35.0,
        design_return_temp_c=30.0,
    )


def test_analyze_building_uses_canonical_registry_heating_zones_by_default():
    model = _model_with_room()
    registry = ensure_mep_registry(model)
    registry.add_heating_zone(_zone("room-1", "hz-1", "radiator"))

    report = analyze_building(model)

    assert report.room_results["room-1"].heating.emitter_type == "radiator"
    assert report.heating_zones == [_zone("room-1", "hz-1", "radiator")]


def test_explicit_heating_zones_override_registry_default():
    model = _model_with_room()
    registry = ensure_mep_registry(model)
    registry.add_heating_zone(_zone("room-1", "hz-registry", "radiator"))

    explicit = _zone("room-1", "hz-explicit", "underfloor")
    report = analyze_building(model, heating_zones=[explicit])

    assert report.room_results["room-1"].heating.emitter_type == "underfloor"
    assert report.heating_zones == [explicit]
