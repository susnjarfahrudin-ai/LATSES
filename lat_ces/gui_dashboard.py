"""Project overview entrypoint layered on the canonical LAT-CES GUI.

The dashboard is a navigation/summary layer only. It never creates a second
BuildingModel; all actions route back into CompleteBuildingWorkspaceApp.
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building_model.quantities import to_quantity_view
from lat_ces.gui_launcher import CompleteBuildingWorkspaceApp


class ProjectOverviewApp(CompleteBuildingWorkspaceApp):
    """Canonical GUI with a first-class project overview/dashboard."""

    def __init__(self) -> None:
        super().__init__()
        self._install_project_overview()
        self._refresh_project_overview()
        self._select_overview_tab()

    def _select_overview_tab(self) -> None:
        for index in range(self.complete_tabs.index("end")):
            if self.complete_tabs.tab(index, "text") == "Pregled projekta":
                self.complete_tabs.select(index)
                return

    def _select_tab(self, title: str) -> None:
        for index in range(self.complete_tabs.index("end")):
            if self.complete_tabs.tab(index, "text") == title:
                self.complete_tabs.select(index)
                self.status_var.set(f"Otvoren prikaz: {title}")
                return

    def _install_project_overview(self) -> None:
        frame = ttk.Frame(self.complete_tabs, padding=14)
        self.complete_tabs.insert(0, frame, text="Pregled projekta")
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(header, text="LAT-CES", font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Label(header, text="  Engineering Workspace", font=("Segoe UI", 11)).pack(side="left", pady=(6, 0))
        ttk.Button(header, text="Osvježi pregled", command=self._refresh_project_overview).pack(side="right")

        left = ttk.LabelFrame(frame, text="Radni tok", padding=12)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)

        steps = (
            ("1", "Reference House", "Model / Pogledi"),
            ("2", "Tlocrt", "Model / Pogledi"),
            ("3", "Presjek", "Model / Pogledi"),
            ("4", "3D", "Model / Pogledi"),
            ("5", "Provjera", "Proračuni"),
            ("6", "Izvještaj", "Engineering Summary"),
            ("7", "Materijali", "Konstrukcija / Statika"),
            ("8", "MEP", "MEP"),
        )
        for row, (number, label, tab_name) in enumerate(steps):
            card = ttk.Frame(left, padding=5)
            card.grid(row=row, column=0, sticky="ew", pady=3)
            ttk.Label(card, text=number, width=3, font=("Segoe UI", 11, "bold")).pack(side="left")
            ttk.Label(card, text=label, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(6, 10))
            ttk.Button(card, text="Otvori", command=lambda title=tab_name: self._select_tab(title)).pack(side="right")

        hint = ttk.Label(left, text="Svi prikazi čitaju isti canonical BuildingModel. Nema zasebnog GUI modela.", wraplength=620)
        hint.grid(row=len(steps), column=0, sticky="w", pady=(10, 0))

        right = ttk.LabelFrame(frame, text="Trenutni model", padding=12)
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        right.rowconfigure(2, weight=1)
        self.overview_identity = ttk.Label(right, font=("Segoe UI", 11, "bold"), wraplength=360)
        self.overview_identity.grid(row=0, column=0, sticky="w")
        self.overview_model = ttk.Label(right, wraplength=360)
        self.overview_model.grid(row=1, column=0, sticky="w", pady=(8, 10))
        self.overview_stats = tk.Text(right, height=18, width=46, wrap="word")
        self.overview_stats.grid(row=2, column=0, sticky="nsew")
        self.overview_stats.configure(state="disabled")

        footer = ttk.Frame(frame)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(footer, text="Otvori tlocrt", command=lambda: self._select_tab("Model / Pogledi")).pack(side="left")
        ttk.Button(footer, text="Provjeri model", command=self.validate_model).pack(side="left", padx=6)
        ttk.Button(footer, text="Model Inspector", command=self.show_canonical_model_inspector).pack(side="left")

    def _refresh_project_overview(self) -> None:
        if not hasattr(self, "overview_identity"):
            return
        model = self.workflow.model
        q = to_quantity_view(model)
        registry = ensure_mep_registry(model)
        self.overview_identity.configure(text=f"{model.name} · {len(model.levels)} etaže")
        self.overview_model.configure(
            text=f"Aktivna etaža: {self.active_level.name}\n"
            f"Gabarit: {self.active_level.length_m:.2f} × {self.active_level.width_m:.2f} m\n"
            f"Visina etaže: {self.active_level.height:.2f} m"
        )
        lines = [
            "OBJEKTI",
            f"Prostorije: {len(q.rooms)}",
            f"Zidovi: {len(q.walls)}",
            f"Otvori: {len(q.openings)}",
            f"Stepeništa: {len(q.stairs)}",
            f"Terase: {len(q.terraces)}",
            f"Materijali/Proizvodi: {len(model.materials)}",
            "",
            "KOLIČINE",
            f"Površina prostorija: {sum(r.floor_area_m2 for r in q.rooms):.2f} m²",
            f"Volumen prostorija: {sum(r.volume_m3 for r in q.rooms):.2f} m³",
            "",
            "MEP",
            f"Ventilacija: {len(registry.all_ventilation_openings)}",
            f"Voda: {len(registry.all_water_branches)}",
            f"Grijanje: {len(registry.all_heating_zones)}",
            "",
            "INTEGRITET",
            "Jedan BuildingModel = source of truth",
        ]
        self.overview_stats.configure(state="normal")
        self.overview_stats.delete("1.0", "end")
        self.overview_stats.insert("1.0", "\n".join(lines))
        self.overview_stats.configure(state="disabled")


def run_dashboard_acceptance() -> None:
    """Deterministic packaged-EXE smoke for the overview dashboard."""
    app = ProjectOverviewApp()
    try:
        tabs = [app.complete_tabs.tab(i, "text") for i in range(app.complete_tabs.index("end"))]
        assert tabs[0] == "Pregled projekta", f"Dashboard not first tab: {tabs}"
        assert app.workflow.model.levels, "Reference House is not loaded"
        assert "Model / Pogledi" in tabs
        assert "Proračuni" in tabs
        assert "Konstrukcija / Statika" in tabs
        assert "MEP" in tabs
        for step, title in ((3, "Tlocrt"), (4, "Presjek"), (5, "3D")):
            app.view_step.set(step)
            app.goto_step()
            app.update_idletasks()
            if not app.canvas.find_all():
                raise RuntimeError(f"{title}: canvas has no rendered content")
        findings = app.workflow.validate()
        if findings:
            raise RuntimeError("Provjera: " + "; ".join(findings))
        app._select_tab("Engineering Summary")
        app.refresh_engineering_summary()
        summary = app.engineering_summary.get("1.0", "end")
        for marker in ("STATIKA", "TERMIKA", "KOLIČINE", "MEP"):
            assert marker in summary, f"Engineering Summary missing {marker}"
        assert app.workflow.model.materials, "Material registry is empty"
        print("GUI DASHBOARD GREEN: overview + Reference House + Tlocrt + Presjek + 3D + Provjera + Izvještaj + Materijali + MEP")
    finally:
        app.destroy()


def main() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") == "1":
        run_dashboard_acceptance()
        return
    ProjectOverviewApp().mainloop()


if __name__ == "__main__":
    main()
