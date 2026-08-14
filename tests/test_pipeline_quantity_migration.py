from lat_ces.core.dimensions import Dimension, LENGTH, MASS, TIME, TEMPERATURE, Unit
from lat_ces.modules.pipeline import FullPlenumSimulation
from lat_ces.scientific.quantities.quantity import PhysicalQuantity


AREA = Dimension(L=2)
FLOW_RATE = Dimension(L=3, T=-1)
DENSITY = Dimension(M=1, L=-3)
SPECIFIC_HEAT = Dimension(L=2, T=-2, Theta=-1)
PRESSURE = Dimension(M=1, L=-1, T=-2)


def test_full_plenum_pipeline_accepts_canonical_physical_quantities():
    meter = Unit("meter", "m", LENGTH)
    area_unit = Unit("square meter", "m2", AREA)
    velocity_unit = Unit("meter per second", "m/s", LENGTH / TIME)
    density_unit = Unit("kilogram per cubic meter", "kg/m3", DENSITY)
    cp_unit = Unit("specific heat", "J/(kg K)", SPECIFIC_HEAT)
    delta_t_unit = Unit("temperature difference", "K", TEMPERATURE)
    pressure_unit = Unit("pascal", "Pa", PRESSURE)

    result = FullPlenumSimulation().run_full_simulation(
        PhysicalQuantity(1.0, 0.0, area_unit),
        PhysicalQuantity(0.5, 0.0, velocity_unit),
        PhysicalQuantity(1.2, 0.0, density_unit),
        0.02,
        PhysicalQuantity(1005.0, 0.0, cp_unit),
        PhysicalQuantity(10.0, 0.0, delta_t_unit),
        PhysicalQuantity(50.0, 0.0, pressure_unit),
    )

    assert result["status"] == "PASS"
    assert result["airflow"].dimension == FLOW_RATE
    assert result["mass_flow"].dimension == Dimension(M=1, T=-1)
    assert result["fan_power"].value > 0
    assert meter.dimension == LENGTH
