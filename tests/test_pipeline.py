import math
from lat_ces.core.dimensions import Dimension
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import AREA, DENSITY, FLOW_RATE, MASS_FLOW
from lat_ces.modules.pipeline import PlenumSystemSimulation


def test_plenum_system_simulation_pass():
    sim = PlenumSystemSimulation(max_allowed_noise_db=50.0)

    area = PhysicalQuantity(1.5, AREA, 0.02)
    velocity = PhysicalQuantity(2.5, Dimension(L=1, T=-1), 0.1)
    density = PhysicalQuantity(1.2, DENSITY, 0.01)

    sound_pressure_pa = 0.002

    report = sim.run_simulation(area, velocity, density, sound_pressure_pa)

    assert report["airflow"].value == 3.75
    assert report["airflow"].dimension == FLOW_RATE
    assert math.isclose(report["mass_flow"].value, 4.5)
    assert report["mass_flow"].dimension == MASS_FLOW
    assert report["noise_acceptable"] is True
    assert report["status"] == "PASS"


def test_plenum_system_simulation_fail_noise():
    sim = PlenumSystemSimulation(max_allowed_noise_db=35.0)

    area = PhysicalQuantity(1.0, AREA, 0.01)
    velocity = PhysicalQuantity(2.0, Dimension(L=1, T=-1), 0.05)
    density = PhysicalQuantity(1.2, DENSITY, 0.01)

    sound_pressure_pa = 1.0

    report = sim.run_simulation(area, velocity, density, sound_pressure_pa)

    assert report["noise_acceptable"] is False
    assert report["status"] == "FAIL"
