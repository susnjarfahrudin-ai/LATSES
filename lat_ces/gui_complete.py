"""Complete LAT-CES desktop workspace."""
from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_engineering import ensure_engineering_results
from lat_ces.building.model import Material, Roof
from lat_ces.building.structural import calculate_structural_loads
from lat_ces.gui import FloorPlanEditor
from lat_ces.gui_drafting import DraftingLATCESApp
from lat_ces.gui_mep_engineering import EngineeringMEPWorkspaceApp


class CompleteBuildingWorkspaceApp(DraftingLATCESApp):
    """One-window BuildingModel workspace with integrated engineering tabs."""

    def __init__(self) -> None:
        self.roof_length_var = self.roof_width_var = None
        self.roof_dead_load_var = self.roof_snow_load_var = None
        self.envelope_finish_var = None
        self.envelope_insulation_material_var = None
        self.envelope_insulation_thickness_var = None
        self.envelope_plaster_material_var = None
        self.envelope_plaster_thickness_var = None
        self.wall_load_bearing_var = None
        self.wall_material_var = None
        self.wall_tributary_var = None
        self.level_dead_load_var = None
        self.level_live_load_var = None
        self.material_name_var = None
        self.material_density_var = None
        self.material_e_var = None
        self.material_lambda_var = None
        self.facade_direction_var = None
        self.calculation_output = None
        self.mep_output = None
        super().__init__()
        self._install_complete_tabs()
        self._refresh_complete_tabs()

    def _install_complete_tabs(self) -> None:
        children = list(self.winfo_children())
        old_steps = next((c for c in children if isinstance(c, ttk.Frame) and any(isinstance(x, ttk.Radiobutton) for x in c.winfo_children())), None)
        body = next((c for c in children if isinstance(c, ttk.Frame) and any(isinstance(x, ttk.LabelFrame) for x in c.winfo_children())), None)
        if old_steps is not None:
            old_steps.pack_forget()
        if body is None:
            return
        self.complete_tabs = ttk.Notebook(self)
        self.complete_tabs.pack(fill="x", padx=18, pady=(0, 8), before=body)
        self.complete_tabs.bind("<<NotebookTabChanged>>", lambda _e: self._refresh_complete_tabs())
        frames = {}
        for key, title in (("model", "Model / Pogledi"), ("envelope", "Omotač / Fasada"), ("structure", "Konstrukcija / Statika"), ("calc", "Proračuni"), ("mep", "MEP"), ("facade", "Fasade")):
            frame = ttk.Frame(self.complete_tabs, padding=8)
            self.complete_tabs.add(frame, text=title)
            frames[key] = frame
        self._build_model_tab(frames["model"])
        self._build_envelope_tab(frames["envelope"])
        self._build_structure_tab(frames["structure"])
        self._build_calc_tab(frames["calc"])
        self._build_mep_tab(frames["mep"])
        self._build_facade_tab(frames["facade"])

    def _build_model_tab(self, tab):
        ttk.Label(tab, text="Pogledi", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        for label, step in (("Krov", 1), ("Sprat", 2), ("Tlocrt", 3), ("Presjek", 4), ("3D", 5)):
            ttk.Button(tab, text=label, command=lambda s=step: self._set_view_step(s)).pack(side="left", padx=2)
        box = ttk.LabelFrame(tab, text="Krovna osnova i opterećenje", padding=8)
        box.pack(side="left", padx=18)
        self.roof_length_var = tk.StringVar(value="10.00")
        self.roof_width_var = tk.StringVar(value="10.00")
        self.roof_dead_load_var = tk.StringVar(value="0.00")
        self.roof_snow_load_var = tk.StringVar(value="0.00")
        for label, var in (("Dužina (m)", self.roof_length_var), ("Širina (m)", self.roof_width_var), ("Stalno (kPa)", self.roof_dead_load_var), ("Snijeg (kPa)", self.roof_snow_load_var)):
            row = ttk.Frame(box); row.pack(fill="x")
            ttk.Label(row, text=label, width=13).pack(side="left")
            ttk.Entry(row, textvariable=var, width=9).pack(side="left", padx=4)
        ttk.Button(box, text="Primijeni krov", command=self.apply_roof).pack(fill="x", pady=(5, 0))

    def _build_envelope_tab(self, tab):
        level = self.active_level
        self.envelope_finish_var = tk.StringVar(value=level.facade_finish)
        self.envelope_insulation_material_var = tk.StringVar(value=level.insulation_material)
        self.envelope_insulation_thickness_var = tk.StringVar(value=f"{level.insulation_thickness_m:.3f}")
        self.envelope_plaster_material_var = tk.StringVar(value=level.interior_plaster_material)
        self.envelope_plaster_thickness_var = tk.StringVar(value=f"{level.interior_plaster_thickness_m:.3f}")
        fields = (("Fasadna završna obrada", self.envelope_finish_var), ("Izolacija — materijal", self.envelope_insulation_material_var), ("Izolacija — debljina (m)", self.envelope_insulation_thickness_var), ("Unutrašnja žbuka — materijal", self.envelope_plaster_material_var), ("Unutrašnja žbuka — debljina (m)", self.envelope_plaster_thickness_var))
        for row, (label, var) in enumerate(fields):
            ttk.Label(tab, text=label).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(tab, textvariable=var, width=34).grid(row=row, column=1, sticky="ew", padx=8, pady=2)
        ttk.Button(tab, text="Primijeni slojeve omotača", command=self._apply_envelope).grid(row=5, column=0, columnspan=2, sticky="ew", pady=7)
        ttk.Label(tab, text="Slojevi ostaju u BuildingModel-u za kasniji termički i energetski proračun.", foreground="#475569").grid(row=6, column=0, columnspan=2, sticky="w")
        tab.columnconfigure(1, weight=1)

    def _build_structure_tab(self, tab):
        self.wall_load_bearing_var = tk.BooleanVar(value=False)
        self.wall_material_var = tk.StringVar(value="")
        self.wall_tributary_var = tk.StringVar(value="0.00")
        self.level_dead_load_var = tk.StringVar(value=f"{self.active_level.dead_load_kpa:.2f}")
        self.level_live_load_var = tk.StringVar(value=f"{self.active_level.live_load_kpa:.2f}")
        ttk.Checkbutton(tab, text="Odabrani zid je NOSIV", variable=self.wall_load_bearing_var).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(tab, text="Materijal").grid(row=1, column=0, sticky="w")
        self.wall_material_combo = ttk.Combobox(tab, textvariable=self.wall_material_var, state="readonly", width=30)
        self.wall_material_combo.grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Label(tab, text="Tributarna širina (m)").grid(row=2, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.wall_tributary_var).grid(row=2, column=1, sticky="ew", padx=8)
        ttk.Button(tab, text="Primijeni zid", command=self._apply_wall_structure).grid(row=3, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Separator(tab).grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(tab, text="Etažno opterećenje").grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Label(tab, text="Stalno q (kPa)").grid(row=6, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.level_dead_load_var).grid(row=6, column=1, sticky="ew", padx=8)
        ttk.Label(tab, text="Korisno q (kPa)").grid(row=7, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.level_live_load_var).grid(row=7, column=1, sticky="ew", padx=8)
        ttk.Button(tab, text="Primijeni opterećenje etaže", command=self._apply_level_loads).grid(row=8, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Separator(tab).grid(row=9, column=0, columnspan=2, sticky="ew", pady=6)
        self.material_name_var = tk.StringVar(value="Armirani beton")
        self.material_density_var = tk.StringVar(value="2500")
        self.material_e_var = tk.StringVar(value="30000000000")
        self.material_lambda_var = tk.StringVar(value="2.10")
        for row, (label, var) in enumerate((("Naziv", self.material_name_var), ("Gustina kg/m³", self.material_density_var), ("E Pa", self.material_e_var), ("λ W/mK", self.material_lambda_var)), start=10):
            ttk.Label(tab, text=label).grid(row=row, column=0, sticky="w")
            ttk.Entry(tab, textvariable=var).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(tab, text="Dodaj materijal", command=self._add_material).grid(row=14, column=0, columnspan=2, sticky="ew", pady=6)
        tab.columnconfigure(1, weight=1)

    def _build_calc_tab(self, tab):
        buttons = ttk.Frame(tab); buttons.pack(fill="x")
        ttk.Button(buttons, text="Statika — preliminarna opterećenja", command=self._calculate_structure).pack(side="left", padx=2)
        ttk.Button(buttons, text="Building Engineering Report", command=self._calculate_building_report).pack(side="left", padx=2)
        ttk.Button(buttons, text="Provjeri model", command=self.validate_model).pack(side="left", padx=2)
        self.calculation_output = tk.Text(tab, height=9, wrap="word"); self.calculation_output.pack(fill="both", expand=True, pady=8); self.calculation_output.configure(state="disabled")
        ttk.Label(tab, text="Statika je u ovoj fazi transparentan load-take-off; konačna projektantska provjera ostaje zaseban standardizirani solver.", foreground="#92400e", wraplength=850).pack(fill="x")

    def _build_mep_tab(self, tab):
        ttk.Button(tab, text="Otvori MEP editor", command=self._open_mep_editor).pack(side="left", padx=2)
        ttk.Button(tab, text="Izračunaj sve MEP", command=self._calculate_building_report).pack(side="left", padx=2)
        ttk.Button(tab, text="Osvježi", command=self._refresh_mep_tab).pack(side="left", padx=2)
        self.mep_output = tk.Text(tab, height=8, wrap="word"); self.mep_output.pack(fill="both", expand=True, pady=8); self.mep_output.configure(state="disabled")

    def _build_facade_tab(self, tab):
        self.facade_direction_var = tk.StringVar(value="Sjever")
        ttk.Label(tab, text="Smjer:").pack(side="left")
        ttk.Combobox(tab, textvariable=self.facade_direction_var, state="readonly", values=("Sjever", "Istok", "Jug", "Zapad"), width=10).pack(side="left", padx=7)
        ttk.Button(tab, text="Prikaži fasadu", command=self._draw_facade).pack(side="left")

    def _set_view_step(self, step):
        self.view_step.set(step); self.goto_step()

    def _apply_envelope(self):
        try:
            level = self.active_level
            level.facade_finish = self.envelope_finish_var.get().strip()
            level.insulation_material = self.envelope_insulation_material_var.get().strip()
            level.insulation_thickness_m = float(self.envelope_insulation_thickness_var.get())
            level.interior_plaster_material = self.envelope_plaster_material_var.get().strip()
            level.interior_plaster_thickness_m = float(self.envelope_plaster_thickness_var.get())
            if level.insulation_thickness_m < 0 or level.interior_plaster_thickness_m < 0: raise ValueError("Debljine slojeva ne mogu biti negativne")
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Omotač", str(exc), parent=self); return
        self.refresh_view(); self.status_var.set("Omotač primijenjen")

    def _apply_level_loads(self):
        try:
            dead, live = float(self.level_dead_load_var.get()), float(self.level_live_load_var.get())
            if dead < 0 or live < 0: raise ValueError("Opterećenja ne mogu biti negativna")
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Statika", str(exc), parent=self); return
        self.active_level.dead_load_kpa = dead; self.active_level.live_load_kpa = live; self.status_var.set("Etažno opterećenje spremljeno")

    def _apply_wall_structure(self):
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        if wall is None:
            messagebox.showinfo("LAT-CES — Konstrukcija", "Prvo odaberi zid na tlocrtu.", parent=self); return
        try:
            tributary = float(self.wall_tributary_var.get())
            if tributary < 0: raise ValueError
        except ValueError:
            messagebox.showwarning("LAT-CES — Konstrukcija", "Tributarna širina mora biti >= 0.", parent=self); return
        wall.load_bearing = bool(self.wall_load_bearing_var.get())
        name = self.wall_material_var.get().strip()
        wall.material_id = next((mid for mid, mat in self.workflow.model.materials.items() if mat.name == name), None)
        wall.tributary_width_m = tributary
        self.refresh_view(); self.status_var.set(f"{wall.role_label}: {wall.name}")

    def _add_material(self):
        try:
            material = Material(name=self.material_name_var.get().strip(), density=float(self.material_density_var.get()), youngs_modulus=float(self.material_e_var.get()), thermal_conductivity=float(self.material_lambda_var.get()))
            self.workflow.model.add_material(material)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Materijal", str(exc), parent=self); return
        self._refresh_structure_materials(); self.status_var.set(f"Materijal dodat: {material.name}")

    def _refresh_structure_materials(self):
        if not hasattr(self, "wall_material_combo"): return
        names = [m.name for m in self.workflow.model.materials.values()]
        self.wall_material_combo["values"] = names
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        if wall and wall.material_id in self.workflow.model.materials: self.wall_material_var.set(self.workflow.model.materials[wall.material_id].name)
        elif not self.wall_material_var.get() and names: self.wall_material_var.set(names[0])

    def _calculate_structure(self):
        report = calculate_structural_loads(self.workflow.model)
        lines = [f"Status: {report.status}", f"Ukupno: {report.total_vertical_line_load_kn_m:.3f} kN/m"]
        if report.findings: lines += ["\nNalazi:"] + [f"- {x}" for x in report.findings]
        lines += [f"{x.wall_name}: {x.line_load_kn_m:.3f} kN/m" for x in report.wall_results]
        self._set_text(self.calculation_output, "\n".join(lines))
        self.status_var.set("Statika izračunata")

    def _calculate_building_report(self):
        result = ensure_engineering_results(self.workflow.model)
        report = build_building_engineering_report(self.workflow.model)
        summary = [f"Building Engineering Report: {report.status}", f"Materijali: {report.material_count}", f"Etaže: {report.level_count}", f"MEP elementi: {report.mep_element_count}", f"Strukturno opterećenje: {result.structural_loads.total_vertical_line_load_kn_m:.3f} kN/m"]
        self._set_text(self.calculation_output, "\n".join(summary))
        self._set_text(self.mep_output, "\n".join(result.mep_findings or ["MEP engineering registry OK"]))
        self.status_var.set("Building engineering rezultati osvježeni")

    @staticmethod
    def _set_text(widget, text: str) -> None:
        widget.configure(state="normal"); widget.delete("1.0", "end"); widget.insert("1.0", text); widget.configure(state="disabled")

    def _open_mep_editor(self):
        EngineeringMEPWorkspaceApp(self, self.workflow.model)

    def _draw_facade(self):
        self.view_step.set(4); self.goto_step(); self.status_var.set(f"Fasada: {self.facade_direction_var.get()}")

    def _refresh_mep_tab(self):
        result = ensure_engineering_results(self.workflow.model)
        self._set_text(self.mep_output, "\n".join(result.mep_findings or ["MEP engineering registry OK"]))

    def _refresh_complete_tabs(self):
        self._refresh_structure_materials()
        self._refresh_mep_tab()


# Keep the canonical application identity explicit for packaging/smoke tests.
def _run_gui_identity_smoke() -> None:
    app = CompleteBuildingWorkspaceApp()
    try:
        if type(app).__name__ != "CompleteBuildingWorkspaceApp":
            raise RuntimeError(f"Unexpected GUI class: {type(app).__name__}")
        expected = ("Model / Pogledi", "Konstrukcija / Statika", "MEP", "Fasade")
        actual = tuple(app.complete_tabs.tab(index, "text") for index in range(app.complete_tabs.index("end")))
        missing = [title for title in expected if title not in actual]
        if missing:
            raise RuntimeError(f"GUI identity check failed; missing tabs: {missing}; actual tabs: {actual}")
        print(f"GUI identity OK: {type(app).__name__}; tabs={actual}")
    finally:
        app.destroy()


def main() -> None:
    if os.environ.get("LATCES_GUI_SMOKE") == "1":
        _run_gui_identity_smoke()
        # Smoke mode must terminate the packaged process explicitly.  Tk and
        # imported GUI components may leave interpreter-level/background work
        # alive after root.destroy(), so sys.exit(0) can leave the PyInstaller
        # process running and make CI report a false timeout.  This is strictly
        # limited to the non-user-facing identity smoke path.
        os._exit(0)
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
