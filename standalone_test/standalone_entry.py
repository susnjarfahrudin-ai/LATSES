"""Standalone field-user application entry point.

This module wraps the isolated standalone runtime with a user-facing
Thermo/Fluid control panel. It remains completely independent from the
production LAT-CES application on main.
"""
from __future__ import annotations

import sys
from PyQt6 import QtCore, QtWidgets
import master_standalone as core


class FahroTerenskaDashboard(core.LATMasterDashboardV3):
    """Field-user dashboard exposing the standalone domain engines."""

    def __init__(self) -> None:
        super().__init__()
        self._install_domain_dock()
        self.log_event("Terenska aplikacija: Thermo/Fluid domeni dostupni kroz panel 'DOMENI'.")

    def _install_domain_dock(self) -> None:
        dock = QtWidgets.QDockWidget("DOMENI – TERMODINAMIKA / FLUIDIKA", self)
        dock.setAllowedAreas(
            QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            | QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        )
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_thermo_panel(), "TERMika")
        tabs.addTab(self._build_fluid_panel(), "FLUID")
        dock.setWidget(tabs)
        self.addDockWidget(QtCore.Qt.DockWidgetArea.RightDockWidgetArea, dock)
        self.domain_dock = dock

    @staticmethod
    def _make_result_box() -> QtWidgets.QPlainTextEdit:
        box = QtWidgets.QPlainTextEdit()
        box.setReadOnly(True)
        box.setMinimumHeight(130)
        return box

    def _build_thermo_panel(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        self.thermo_n = QtWidgets.QDoubleSpinBox()
        self.thermo_n.setRange(0.000001, 1_000_000.0)
        self.thermo_n.setValue(10.0)
        self.thermo_n.setSuffix(" mol")

        self.thermo_temp = QtWidgets.QDoubleSpinBox()
        self.thermo_temp.setRange(0.0, 10_000.0)
        self.thermo_temp.setValue(300.0)
        self.thermo_temp.setSuffix(" K")

        self.thermo_volume = QtWidgets.QDoubleSpinBox()
        self.thermo_volume.setRange(0.000001, 1_000_000.0)
        self.thermo_volume.setValue(0.5)
        self.thermo_volume.setSuffix(" m³")

        self.thermo_k = QtWidgets.QDoubleSpinBox()
        self.thermo_k.setRange(0.000001, 10_000.0)
        self.thermo_k.setValue(0.8)
        self.thermo_k.setSuffix(" W/mK")

        self.thermo_dx = QtWidgets.QDoubleSpinBox()
        self.thermo_dx.setRange(0.000001, 100.0)
        self.thermo_dx.setValue(0.15)
        self.thermo_dx.setSuffix(" m")

        self.thermo_th = QtWidgets.QDoubleSpinBox()
        self.thermo_th.setRange(-10_000.0, 10_000.0)
        self.thermo_th.setValue(25.0)
        self.thermo_th.setSuffix(" °C")

        self.thermo_tl = QtWidgets.QDoubleSpinBox()
        self.thermo_tl.setRange(-10_000.0, 10_000.0)
        self.thermo_tl.setValue(20.0)
        self.thermo_tl.setSuffix(" °C")

        self.thermo_result = self._make_result_box()
        run_gas = QtWidgets.QPushButton("Izračunaj idealni gas P = nRT/V")
        run_flux = QtWidgets.QPushButton("Izračunaj toplotni tok q = k·ΔT/dx")
        run_gas.clicked.connect(self._run_ideal_gas)
        run_flux.clicked.connect(self._run_heat_flux)

        layout.addRow("Količina supstance", self.thermo_n)
        layout.addRow("Temperatura", self.thermo_temp)
        layout.addRow("Zapremina", self.thermo_volume)
        layout.addRow(run_gas)
        layout.addRow("Toplotna provodljivost", self.thermo_k)
        layout.addRow("Debljina", self.thermo_dx)
        layout.addRow("T visoka", self.thermo_th)
        layout.addRow("T niska", self.thermo_tl)
        layout.addRow(run_flux)
        layout.addRow("Rezultat", self.thermo_result)
        return widget

    def _build_fluid_panel(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)

        self.fluid_density = QtWidgets.QDoubleSpinBox()
        self.fluid_density.setRange(0.0, 100_000.0)
        self.fluid_density.setValue(1000.0)
        self.fluid_density.setSuffix(" kg/m³")

        self.fluid_depth = QtWidgets.QDoubleSpinBox()
        self.fluid_depth.setRange(0.0, 10_000.0)
        self.fluid_depth.setValue(5.0)
        self.fluid_depth.setSuffix(" m")

        self.fluid_surface = QtWidgets.QDoubleSpinBox()
        self.fluid_surface.setRange(0.0, 100_000_000.0)
        self.fluid_surface.setValue(101325.0)
        self.fluid_surface.setSuffix(" Pa")

        self.fluid_velocity = QtWidgets.QDoubleSpinBox()
        self.fluid_velocity.setRange(-100_000.0, 100_000.0)
        self.fluid_velocity.setValue(2.0)
        self.fluid_velocity.setSuffix(" m/s")

        self.fluid_length = QtWidgets.QDoubleSpinBox()
        self.fluid_length.setRange(0.000001, 10_000.0)
        self.fluid_length.setValue(0.05)
        self.fluid_length.setSuffix(" m")

        self.fluid_viscosity = QtWidgets.QDoubleSpinBox()
        self.fluid_viscosity.setRange(0.000000001, 1000.0)
        self.fluid_viscosity.setValue(0.001)
        self.fluid_viscosity.setDecimals(6)
        self.fluid_viscosity.setSuffix(" Pa·s")

        self.fluid_result = self._make_result_box()
        run_hydro = QtWidgets.QPushButton("Izračunaj hidrostatički pritisak")
        run_re = QtWidgets.QPushButton("Izračunaj Reynoldsov broj")
        run_hydro.clicked.connect(self._run_hydrostatic)
        run_re.clicked.connect(self._run_reynolds)

        layout.addRow("Gustina", self.fluid_density)
        layout.addRow("Dubina", self.fluid_depth)
        layout.addRow("Površinski pritisak", self.fluid_surface)
        layout.addRow(run_hydro)
        layout.addRow("Brzina", self.fluid_velocity)
        layout.addRow("Karakteristična dužina", self.fluid_length)
        layout.addRow("Dinamička viskoznost", self.fluid_viscosity)
        layout.addRow(run_re)
        layout.addRow("Rezultat", self.fluid_result)
        return widget

    def _run_ideal_gas(self) -> None:
        try:
            pressure = core.HardenedThermodynamicsEngine.compute_ideal_gas_pressure(
                self.thermo_n.value(), self.thermo_temp.value(), self.thermo_volume.value()
            )
            self.thermo_result.setPlainText(f"Idealni gas pressure: {pressure:.6f} Pa")
            self.log_event(f"TERMika: P = {pressure:.6f} Pa")
        except Exception as exc:
            self.thermo_result.setPlainText(f"GREŠKA: {exc}")

    def _run_heat_flux(self) -> None:
        try:
            flux = core.HardenedThermodynamicsEngine.compute_conduction_heat_flux(
                self.thermo_k.value(),
                self.thermo_dx.value(),
                self.thermo_th.value(),
                self.thermo_tl.value(),
            )
            self.thermo_result.setPlainText(f"Heat flux: {flux:.6f} W/m²")
            self.log_event(f"TERMika: q = {flux:.6f} W/m²")
        except Exception as exc:
            self.thermo_result.setPlainText(f"GREŠKA: {exc}")

    def _run_hydrostatic(self) -> None:
        try:
            pressure = core.HardenedFluidMechanicsEngine.compute_hydrostatic_pressure(
                self.fluid_density.value(), self.fluid_depth.value(), self.fluid_surface.value()
            )
            self.fluid_result.setPlainText(f"Hydrostatic pressure: {pressure:.6f} Pa")
            self.log_event(f"FLUID: P = {pressure:.6f} Pa")
        except Exception as exc:
            self.fluid_result.setPlainText(f"GREŠKA: {exc}")

    def _run_reynolds(self) -> None:
        try:
            reynolds = core.HardenedFluidMechanicsEngine.compute_reynolds_number(
                self.fluid_density.value(),
                self.fluid_velocity.value(),
                self.fluid_length.value(),
                self.fluid_viscosity.value(),
            )
            self.fluid_result.setPlainText(f"Reynolds number: {reynolds:.6f}")
            self.log_event(f"FLUID: Re = {reynolds:.6f}")
        except Exception as exc:
            self.fluid_result.setPlainText(f"GREŠKA: {exc}")


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


def verify_gui_domain_access() -> bool:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = FahroTerenskaDashboard()
    window._run_ideal_gas()
    assert "Pa" in window.thermo_result.toPlainText()
    window._run_heat_flux()
    assert "W/m²" in window.thermo_result.toPlainText()
    window._run_hydrostatic()
    assert "Pa" in window.fluid_result.toPlainText()
    window._run_reynolds()
    assert "Reynolds number:" in window.fluid_result.toPlainText()
    window.close()
    return True


def verify_all() -> bool:
    return (
        core.execute_master_runtime_verification()
        and core.execute_domain_extension_verification_suite()
        and execute_domain_and_mep_verification_suite()
        and verify_gui_domain_access()
    )


def main() -> int:
    if not verify_all():
        return 1
    app = QtWidgets.QApplication(sys.argv)
    dashboard = FahroTerenskaDashboard()
    dashboard.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
