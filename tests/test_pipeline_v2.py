import math
from lat_ces.core.dimensions import Dimension
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import AREA, DENSITY, FLOW_RATE, MASS_FLOW
from lat_ces.modules.thermal import SPECIFIC_HEAT, TEMPERATURE, HEAT_RATE
from lat_ces.modules.pressure import PRESSURE, POWER
from lat_ces.modules.pipeline import FullPlenumSimulation


def test_full_plenum_simulation():
    sim = FullPlenumSimulation(max_allowed_noise_db=50.0, fan_efficiency=0.8)

    area = PhysicalQuantity(2.0, AREA, 0.05)
    velocity = PhysicalQuantity(3.0, Dimension(L=1, T=-1), 0.1)
    density = PhysicalQuantity(1.2, DENSITY, 0.01)
    sound_pressure_pa = 0.002
    cp = PhysicalQuantity(1005.0, SPECIFIC_HEAT, 5.0)
    delta_T = PhysicalQuantity(10.0, TEMPERATURE, 0.2)
    dp = PhysicalQuantity(200.0, PRESSURE, 10.0)

    report = sim.run_full_simulation(
        area=area,
        velocity=velocity,
        density=density,
        sound_pressure_pa=sound_pressure_pa,
        specific_heat=cp,
        delta_temp=delta_T,
        pressure_drop=dp
    )

    assert report["airflow"].value == 6.0
    assert report["airflow"].dimension == FLOW_RATE

    assert math.isclose(report["mass_flow"].value, 7.2)
    assert report["mass_flow"].dimension == MASS_FLOW

    assert report["noise_acceptable"] is True

    assert math.isclose(report["heat_rate"].value, 72360.0)
    assert report["heat_rate"].dimension == HEAT_RATE

    assert math.isclose(report["fan_power"].value, 1500.0)
    assert report["fan_power"].dimension == POWER

    assert report["status"] == "PASS"
