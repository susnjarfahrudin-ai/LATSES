from lat_ces.building.mep import (
    HEATING_EMITTERS,
    HEATING_SOURCES,
    HeatingZone,
    UnderfloorHeatingSystem,
)


def test_heating_source_catalog_contains_required_options() -> None:
    required = {
        "heat_pump_air_water",
        "heat_pump_air_air",
        "ground_source_heat_pump",
        "water_source_heat_pump",
        "gas_boiler",
        "oil_boiler",
        "pellet_boiler",
        "pellet_stove",
        "wood_biomass_boiler",
        "district_heating",
        "electric_boiler",
        "electric_direct",
        "infrared",
        "solar_thermal",
        "hybrid",
    }
    assert required <= set(HEATING_SOURCES)


def test_heating_emitter_catalog_contains_required_options() -> None:
    required = {
        "underfloor",
        "radiator",
        "fan_coil",
        "air_conditioner",
        "wall_heating",
        "ceiling_heating",
        "convector",
        "electric_panel",
        "infrared_panel",
        "heated_towel_rail",
        "air",
        "combined",
    }
    assert required <= set(HEATING_EMITTERS)


def test_heating_zone_separates_source_from_emitter() -> None:
    zone = HeatingZone(
        id="HZ-1",
        room_id="ROOM-1",
        emitter_type="radiator",
        source_type="pellet_boiler",
        design_supply_temp_c=60.0,
        design_return_temp_c=45.0,
    )
    assert zone.source_type == "pellet_boiler"
    assert zone.emitter_type == "radiator"


def test_underfloor_system_carries_source_and_layer_products() -> None:
    system = UnderfloorHeatingSystem(
        id="UFH-1",
        room_id="ROOM-1",
        level_id="LVL-1",
        pipe_product_id="UFH-PEX-16X2",
        pipe_spacing_m=0.15,
        insulation_product_id="INSULATION-EPS",
        insulation_thickness_m=0.05,
        screed_product_id="SCREED-REFERENCE",
        screed_thickness_m=0.05,
        finish_product_id="TILE-GRES-10MM",
        finish_thickness_m=0.01,
        source_type="heat_pump_air_water",
        source_product_id="HP-REFERENCE",
    )
    assert system.pipe_spacing_m == 0.15
    assert system.source_type == "heat_pump_air_water"
    assert system.insulation_thickness_m == 0.05
    assert system.screed_thickness_m == 0.05
    assert system.finish_thickness_m == 0.01
