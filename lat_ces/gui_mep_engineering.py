"""Unified MEP GUI with engineering calculation dispatch and result display."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_engineering import MEPEngineeringService, ensure_engineering_results
from lat_ces.gui_mep_workspace import UnifiedMEPWorkspaceApp


class EngineeringMEPWorkspaceApp(UnifiedMEPWorkspaceApp):
    """Unified MEP selector plus engineering calculation/result presentation."""

    def __init__(self) -> None:
        self.engineering_service = MEPEngineeringService()
        self.engineering_result_var: tk.StringVar | None = None
        super().__init__()

    def _build_side_panel(self, side: ttk.Frame) -> None:
        super()._build_side_panel(side)
        box = ttk.LabelFrame(side, text="MEP — engineering", padding=8)
        box.pack(fill="x", pady=(10, 0), before=self.heating_list.master)
        ttk.Button(box, text="⚙ Izračunaj odabrani", command=self._calculate_selected_mep).pack(fill="x")
        self.engineering_result_var = tk.StringVar(master=self, value="Nema rezultata")
        ttk.Label(box, textvariable=self.engineering_result_var, wraplength=330, justify="left").pack(fill="x", pady=(8, 0))

    def _selected_object(self):
        if self.mep_selected_ref is None:
            raise ValueError("Prvo odaberi MEP objekat")
        object_type, object_id = self.mep_selected_ref
        registry = ensure_mep_registry(self.workflow.model)
        if object_type == "ventilation":
            return object_type, object_id, registry.ventilation_openings[object_id]
        if object_type == "water":
            return object_type, object_id, registry.water_branches[object_id]
        return object_type, object_id, registry.heating_zones[object_id]

    def _calculate_selected_mep(self) -> None:
        try:
            object_type, object_id, obj = self._selected_object()
            result = self.engineering_service.calculate(object_type, obj)
            registry = ensure_mep_registry(self.workflow.model)
            ensure_engineering_results(registry).put(result)
        except (KeyError, TypeError, ValueError) as exc:
            messagebox.showwarning("LAT-CES — Engineering", str(exc), parent=self)
            return
        text = f"{result.status}\n{result.message}\n{self._format_values(result.values)}"
        if self.engineering_result_var is not None:
            self.engineering_result_var.set(text)
        self.status_var.set(f"Engineering rezultat: {object_type} · {object_id} · {result.status}")

    def _build_report(self) -> None:
        try:
            report = build_building_engineering_report(self.workflow.model, service=self.engineering_service)
        except (KeyError, TypeError, ValueError) as exc:
            messagebox.showwarning("LAT-CES — Engineering Report", str(exc), parent=self)
            return
        text = (
            f"STATUS: {report.status}\n"
            f"Objekata: {report.result_count} · CALCULATED: {report.calculated_count}\n"
            f"INPUT_REQUIRED: {report.input_required_count} · CONFLICT: {report.conflict_count}\n"
            f"Ukupan dovod zraka: {report.total_ventilation_flow_m3_h:.2f} m³/h\n"
            f"Ukupno grijanje: {report.total_heating_load_w:.2f} W\n"
            f"Ukupan pad pritiska vode: {report.total_water_pressure_drop_pa:.2f} Pa"
        )
        if self.engineering_report_var is not None:
            self.engineering_report_var.set(text)
        self.status_var.set(f"Building Engineering Report: {report.status}")

    def _select_unified_mep(self, _event: tk.Event | None = None) -> None:
        super()._select_unified_mep(_event)
        if self.mep_selected_ref is None or self.engineering_result_var is None:
            return
        object_type, object_id = self.mep_selected_ref
        result = ensure_engineering_results(ensure_mep_registry(self.workflow.model)).get(object_type, object_id)
        if result is None:
            self.engineering_result_var.set("Nema spremljenog engineering rezultata za odabrani objekat.")
            return
        values = "\n".join(f"{key}: {value:.6g}" if isinstance(value, float) else f"{key}: {value}" for key, value in result.values.items())
        self.engineering_result_var.set(f"{result.status}\n{result.message}\n{values}")

    def _delete_unified_mep(self) -> None:
        selected = self.mep_selected_ref
        super()._delete_unified_mep()
        if selected:
            ensure_engineering_results(ensure_mep_registry(self.workflow.model)).remove(*selected)
        if self.engineering_result_var is not None:
            self.engineering_result_var.set("Nema rezultata")


def main() -> None:
    EngineeringMEPWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
