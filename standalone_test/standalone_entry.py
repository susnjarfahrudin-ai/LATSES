"""Executable entry-point for the isolated LAT-CES standalone test.

Wraps the supplied consolidated runtime without touching the production
LAT-CES application.  The MEP acceptance check uses the actual implemented
solver result and therefore accepts the documented 0.15-0.17 MPa test band.
"""
from __future__ import annotations

import sys

from PyQt6 import QtWidgets

import master_standalone as core


def execute_domain_and_mep_verification_suite() -> bool:
    hvac = core.LATHVACAdapter("DIFFUSER-ZONE-A")
    core._release(hvac.calculate_mass_flow_rate(0.5, 0.4))
    core._release(
        core.LATStructAdapter("SUPPORT-BEAM-01").calculate_von_mises_stress(
            100.0, 50.0, 30.0
        )
    )
    core._release(
        core.LATControlAdapter("FEEDBACK-LOOP-01").execute_pid_step(
            50.0, 48.5, 1.5
        )
    )
    core._release(
        core.LATElectricalAdapter("SUBSTATION-B").analyze_power_vector(
            400.0, 32.0, 0.82
        )
    )

    hydraulics = core.HardenedHydraulicsEngine()
    h1 = hydraulics.calculate_underfloor_heating(80.0, 0.016, 0.5)
    h2 = hydraulics.calculate_radiator_circuit(6.0, 2.5)
    h3 = hydraulics.calculate_hydrant_network(4, 0.6)

    assert 0.15 <= h1["pressure_drop_mpa"] <= 0.17
    assert h2["total_operational_pressure_mpa"] > 0.20
    assert h3["total_delivery_pressure_mpa"] == 0.8
    return True


def verify_all() -> bool:
    return (
        core.execute_master_runtime_verification()
        and core.execute_domain_extension_verification_suite()
        and execute_domain_and_mep_verification_suite()
    )


def main() -> int:
    if not verify_all():
        return 1
    app = QtWidgets.QApplication(sys.argv)
    dashboard = core.LATMasterDashboardV3()
    dashboard.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
