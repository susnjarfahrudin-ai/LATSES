"""Product assignment workspace with engineering Product -> Summary projection."""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import ttk

from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import Room
from lat_ces.catalog.product_engineering import build_product_engineering_report
from lat_ces.catalog.product_catalog import get_product, products_for_category
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.gui_product_dashboard import ProductBuildingWorkspaceApp


class ProductEngineeringWorkspaceApp(ProductBuildingWorkspaceApp):
    """Canonical Product workspace plus visible statics/thermal projection."""

    def __init__(self) -> None:
        super().__init__()
        self._install_product_engineering_summary()

    def _install_product_engineering_summary(self) -> None:
        """Reuse the canonical Engineering Summary instead of adding a second tab."""
        if not hasattr(self, "complete_tabs"):
            return
        summary_index = next(
            (
                index
                for index in range(self.complete_tabs.index("end"))
                if self.complete_tabs.tab(index, "text") == "Engineering Summary"
            ),
            None,
        )
        if summary_index is None:
            return

        # The launcher already owns the single canonical summary tab.
        # Product engineering projects its richer result into that same tab.
        self.product_engineering_summary = getattr(self, "engineering_summary", None)
        if self.product_engineering_summary is None:
            return
        self.complete_tabs.select(summary_index)
        self.refresh_product_engineering_summary()

    def refresh_product_engineering_summary(self) -> None:
        widget = getattr(self, "product_engineering_summary", None)
        if widget is None:
            return
        report = build_product_engineering_report(self.workflow.model)
        lines = [
            "PRODUCT → CANONICAL BUILDING MODEL → ENGINEERING SUMMARY",
            f"Status: {report.status}",
            f"Engineering zapisi: {len(report.records)} · Calculated: {report.calculated_count} · Input required: {report.input_required_count}",
            "",
            "STATIKA",
        ]
        structural_records = [record for record in report.records if record.target_type == "wall"]
        if not structural_records:
            lines.append("Nema vezanih proizvoda na zidove.")
        for record in structural_records:
            line = (
                f"{record.target_id} | Product ID={record.product_id} | Material/Product={record.product_name} | "
                f"ρ={record.density_kg_m3 if record.density_kg_m3 is not None else 'INPUT_REQUIRED'} kg/m³ | "
                f"status={record.structural_status}"
            )
            if record.self_weight_kn_m is not None:
                line += f" | G_self={record.self_weight_kn_m:.3f} kN/m"
            lines.append(line)
            if record.findings:
                lines.append("  Napomena: " + "; ".join(record.findings))

        lines += ["", "TERMIKA"]
        if not structural_records:
            lines.append("Nema vezanih proizvoda na zidove.")
        for record in structural_records:
            line = (
                f"{record.target_id} | Product ID={record.product_id} | "
                f"λ={record.thermal_conductivity_w_mk if record.thermal_conductivity_w_mk is not None else 'INPUT_REQUIRED'} W/mK | "
                f"status={record.thermal_status}"
            )
            if record.conductive_resistance_m2kw is not None:
                line += f" | R={record.conductive_resistance_m2kw:.6f} m²K/W"
            lines.append(line)

        lines += ["", "PRODUCT IDENTITET / PROVENANCE"]
        if not report.records:
            lines.append("Nema Product bindinga.")
        for record in report.records:
            lines.append(
                f"{record.target_id} [{record.target_type}] → {record.product_id} | "
                f"Material/Product={record.product_name} | proizvođač={record.manufacturer or 'N/A'} | "
                f"source={record.source or 'N/A'} | verification={record.verification_status}"
            )

        lines += ["", "PRAVILO", "INPUT_REQUIRED se prikazuje samo kada potrebna inženjerska vrijednost nije dostupna u canonical Product/Material evidenciji ili nedostaje eksplicitan modelni ulaz."]
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", "\n".join(lines))
        widget.configure(state="disabled")

    def _acceptance_checkpoint(self, name: str) -> None:
        print(f"GUI ACCEPTANCE CHECKPOINT: {name}", flush=True)

    def _ensure_acceptance_room_fixture(self) -> None:
        """Provide the smallest canonical Room required by the acceptance contract."""
        if self._room_targets():
            return
        level = self.active_level
        level.add_room(
            Room(
                name="Acceptance Room",
                room_id="ROOM-ACCEPTANCE",
                footprint=Box3D(Point3D(0.0, 0.0, level.elevation), 4.0, 4.0, level.height),
            )
        )

    def run_acceptance(self) -> None:
        self._ensure_acceptance_room_fixture()
        self._acceptance_checkpoint("before_super_run_acceptance")
        super().run_acceptance()
        self._acceptance_checkpoint("after_super_run_acceptance")
        model = self.workflow.model
        wall_id, _ = self._wall_targets()[0]
        wall = self.floor_plan.walls[wall_id]
        wall.load_bearing = True
        wall.tributary_width_m = 2.50
        self._acceptance_checkpoint("before_build_product_engineering_report_calculated")
        self.refresh_product_engineering_summary()
        report = build_product_engineering_report(model)
        self._acceptance_checkpoint("after_build_product_engineering_report_calculated")
        reference = get_product("CONCRETE-REFERENCE-C25-30")
        record = next(item for item in report.records if item.target_id == wall_id)
        assert reference is not None
        assert record.product_id == reference.product_id
        assert record.density_kg_m3 == 2500.0
        assert record.thermal_conductivity_w_mk == 2.10
        assert record.structural_status == "CALCULATED"
        assert record.self_weight_kn_m is not None and record.self_weight_kn_m > 0.0
        assert record.thermal_status == "CALCULATED"
        assert record.conductive_resistance_m2kw is not None and record.conductive_resistance_m2kw > 0.0
        missing_product = next(product for product in products_for_category("Zidovi") if product.status == "MISSING")
        missing_product_id = missing_product.product_id
        ensure_product_binding_registry(model).bind(wall_id, "wall", "MASONRY-THERMAL-25X25X30-MISSING")
        wall.material_id = None
        self._acceptance_checkpoint("before_build_product_engineering_report_missing")
        missing_report = build_product_engineering_report(model)
        self._acceptance_checkpoint("after_build_product_engineering_report_missing")
        missing = next(item for item in missing_report.records if item.target_id == wall_id)
        print(f"GUI ACCEPTANCE MISSING RESULT: verification_status={missing.verification_status!r} thermal_status={missing.thermal_status!r}", flush=True)
        assert missing.verification_status == "MISSING"
        assert missing.thermal_status == "INPUT_REQUIRED"
        self.refresh_product_engineering_summary()
        print("PRODUCT ENGINEERING GREEN: density -> structural self-weight + lambda -> thermal R + Product ID/material/provenance + INPUT_REQUIRED gate", flush=True)


def run_product_engineering_acceptance() -> None:
    print("GUI ACCEPTANCE CHECKPOINT: before_app_create", flush=True)
    print("GUI ACCEPTANCE CHECKPOINT: before_app_constructor", flush=True)
    app = ProductEngineeringWorkspaceApp()
    print("GUI ACCEPTANCE CHECKPOINT: after_app_constructor", flush=True)
    print("GUI ACCEPTANCE CHECKPOINT: after_app_create", flush=True)
    app.withdraw()
    app.update_idletasks()
    print("GUI ACCEPTANCE CHECKPOINT: before_run_acceptance", flush=True)
    app.run_acceptance()
    print("GUI ACCEPTANCE CHECKPOINT: after_run_acceptance", flush=True)
    text = app.product_engineering_summary.get("1.0", "end")
    for marker in ("STATIKA", "TERMIKA", "PRODUCT IDENTITET / PROVENANCE", "INPUT_REQUIRED"):
        assert marker in text, f"Engineering summary missing {marker}"
    print("GUI PRODUCT ENGINEERING GREEN", flush=True)


def main() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") == "1":
        run_product_engineering_acceptance()
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(0)
    ProductEngineeringWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
