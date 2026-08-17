import math
from lat_ces.core.dimensions import VELOCITY, LENGTH, DENSITY
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.modules.plenum import AREA
from lat_ces.modules.pipeline_v3 import DuctNetworkSimulation


def test_full_network_simulation():
    sim = DuctNetworkSimulation(max_allowed_pressure_pa=500.0)

    area = PhysicalQuantity(1.0, AREA, 0.02)
    velocity = PhysicalQuantity(3.0, VELOCITY, 0.1)
    density = PhysicalQuantity(1.2, DENSITY, 0.01)
    duct_length = PhysicalQuantity(20.0, LENGTH, 0.2)
    d_h = PhysicalQuantity(0.5, LENGTH, 0.01)
    fitting_zeta_sum = 1.5
    temp_c = 22.0
    v_press = 1200.0

    report = sim.run_network_simulation(
        area, velocity, density, duct_length, d_h, fitting_zeta_sum, temp_c, v_press
    )

    assert report["airflow"].value == 3.0
    assert report["reynolds"] > 2300.0
    assert report["total_dp"].value > 0
    assert report["fan_power"].value > 0
    assert 0.0 <= report["relative_humidity"] <= 100.0
    assert report["status"] == "PASS"
