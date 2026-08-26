from lat_ces.thermal import (
    CalculationScope,
    InputStatus,
    IndoorConditionInput,
    InternalGainsInput,
    MaterialThermalInput,
    ThermalZoneInput,
    WeatherInput,
    build_actions,
    validate_thermal_inputs,
)


def _valid_zone() -> ThermalZoneInput:
    return ThermalZoneInput(
        zone_id="zone-1",
        scope=CalculationScope.DESIGN_HEATING,
        material_layers=[
            MaterialThermalInput(
                material_id="wall-layer-1",
                thickness_m=0.15,
                conductivity_w_mk=0.035,
                density_kg_m3=100.0,
                heat_capacity_j_kgk=1030.0,
                source_ref="manufacturer-1",
            )
        ],
        weather=WeatherInput(design_outdoor_temp_c=-12.0),
        indoor=IndoorConditionInput(design_indoor_temp_c=21.0, ventilation_ach=0.5),
        internal_gains=InternalGainsInput(gains_w_m2=4.0),
    )


def test_complete_design_heating_inputs_are_ready():
    result = validate_thermal_inputs(_valid_zone())
    assert result.status is InputStatus.PRESENT
    assert result.calculation_allowed is True
    assert result.missing_parameters == []


def test_missing_required_input_blocks_calculation_and_creates_action():
    zone = _valid_zone()
    zone = ThermalZoneInput(
        zone_id=zone.zone_id,
        scope=zone.scope,
        material_layers=zone.material_layers,
        weather=zone.weather,
        indoor=IndoorConditionInput(design_indoor_temp_c=21.0),
        internal_gains=zone.internal_gains,
    )
    result = validate_thermal_inputs(zone)
    assert result.status is InputStatus.MISSING
    assert result.calculation_allowed is False

    actions = build_actions(result, project_id="project-1", zone_id="zone-1")
    assert actions
    assert all(action.kind == "INPUT_BLOCKER" for action in actions)


def test_thermal_bridge_scope_requires_length_and_psi():
    from lat_ces.thermal import ThermalBridgeInput

    zone = _valid_zone()
    zone = ThermalZoneInput(
        zone_id=zone.zone_id,
        scope=CalculationScope.THERMAL_BRIDGE,
        material_layers=zone.material_layers,
        thermal_bridges=[ThermalBridgeInput(bridge_id="tb-1")],
        weather=zone.weather,
        indoor=zone.indoor,
        internal_gains=zone.internal_gains,
    )
    result = validate_thermal_inputs(zone)
    fields = {item.field for item in result.missing_parameters}
    assert "length_m" in fields
    assert "psi_value_w_mk" in fields
