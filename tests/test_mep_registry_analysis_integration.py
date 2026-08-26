from lat_ces.building_model.integration import analyze_building
from lat_ces.building_model.core import BuildingModel, Level, Room
from lat_ces.building.mep import HeatingZone, ensure_mep_registry


def _model_with_room():
    model = BuildingModel(name="MEP integration")
    level = Level(name="Ground", elevation_m=0.0)
    level.add_room(Room(name="Living", length_m=5.0, width_m=4.0, height_m=2.8))
    model.add_level(level)
    return model


def test_analyze_building_uses_canonical_registry_heating_zones_by_default():
    model = _model_with_room()
    registry = ensure_mep_registry(model)
    registry.add_heating_zone(
        HeatingZone(
            id="hz-1",
            room_id=model.levels[0].rooms[0].id,
            emitter_type="radiator",
        )
    )

    report = analyze_building(model)

    assert report.room_results[0].emitter_type == "radiator"


def test_explicit_heating_zones_override_registry_default():
    model = _model_with_room()
    registry = ensure_mep_registry(model)
    registry.add_heating_zone(
        HeatingZone(
            id="hz-registry",
            room_id=model.levels[0].rooms[0].id,
            emitter_type="radiator",
        )
    )

    explicit = HeatingZone(
        id="hz-explicit",
        room_id=model.levels[0].rooms[0].id,
        emitter_type="floor_heating",
    )
    report = analyze_building(model, heating_zones=[explicit])

    assert report.room_results[0].emitter_type == "floor_heating"
