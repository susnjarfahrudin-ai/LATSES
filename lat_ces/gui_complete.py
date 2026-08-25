"""Complete LAT-CES desktop workspace."""
from __future__ import annotations

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
from lat_ces.reference_house_workflow import build_reference_house_workflow


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

    def _build_side_panel(self, side: ttk.Frame) -> None:
        side.configure(width=320)
        quick = ttk.LabelFrame(side, text="Brzi pristup", padding=8)
        quick.pack(fill="x", pady=(0, 8))
        ttk.Button(quick, text="Referentna kuća", command=self.open_reference_house).pack(fill="x")
        draft = ttk.Frame(quick)
        draft.pack(fill="x", pady=(6, 0))
        for text, command in (("Tlocrt", lambda: self._set_view_step(3)), ("Zid", self._open_wall_editor), ("Prostorija", lambda: self._start_payload("room")), ("Vrata", lambda: self._start_payload("door")), ("Prozor", lambda: self._start_payload("window"))):
            ttk.Button(draft, text=text, command=command).pack(side="left", expand=True, fill="x", padx=2)
        super()._build_side_panel(side)

    def open_reference_house(self) -> None:
        try:
            self.workflow = build_reference_house_workflow()
            self.editor = FloorPlanEditor(self)
            self.model_path.set("")
            self.view_step.set(3)
            self.configure_stage(3)
            self.refresh_view()
            self.status_var.set("Referentna kuća učitana — P+3 · 12 × 10 m")
        except Exception as exc:
            messagebox.showerror(
                "LAT-CES — Referentna kuća",
                f"Referentna kuća se ne može učitati.\n\n{exc}",
                parent=self,
            )

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
        lines += [f"{x.wall_name} · vlastita {x.self_weight_kn_m:.3f} · etaža {x.tributary_floor_load_kn_m:.3f} · krov {x.tributary_roof_load_kn_m:.3f} · ukupno {x.total_line_load_kn_m:.3f} kN/m" for x in report.walls]
        self._set_text(self.calculation_output, "\n".join(lines))

    def _calculate_building_report(self):
        report = build_building_engineering_report(self.workflow.model)
        self._set_text(self.calculation_output, "\n".join((f"Status: {report.status}", f"Rezultata: {report.result_count}", f"CALCULATED: {report.calculated_count}", f"INPUT_REQUIRED: {report.input_required_count}", f"INPUT_CONFLICT: {report.conflict_count}", f"Ventilacija: {report.total_ventilation_flow_m3_h:.3f} m³/h", f"Grijanje: {report.total_heating_load_w:.3f} W", f"Voda: {report.total_water_pressure_drop_pa:.3f} Pa")))
        self._refresh_mep_tab()

    def _refresh_mep_tab(self):
        if self.mep_output is None: return
        registry = ensure_mep_registry(self.workflow.model); results = ensure_engineering_results(registry)
        lines = [f"Ventilacija: {len(registry.all_ventilation_openings)}", f"Voda: {len(registry.all_water_branches)}", f"Grijanje: {len(registry.all_heating_zones)}"] + [f"{r.object_type}:{r.object_id} → {r.status}" for r in results.all]
        self._set_text(self.mep_output, "\n".join(lines))

    def _open_mep_editor(self):
        try:
            app = EngineeringMEPWorkspaceApp()
            app.workflow = self.workflow
            app.editor = FloorPlanEditor(app)
            app.refresh_view()
            app.title("LAT-CES — MEP Engineering — trenutni BuildingModel")
            app.mainloop()
        except Exception as exc:
            messagebox.showerror("LAT-CES — MEP", str(exc), parent=self)

    @staticmethod
    def _set_text(widget, value):
        widget.configure(state="normal"); widget.delete("1.0", "end"); widget.insert("1.0", value); widget.configure(state="disabled")

    def _refresh_complete_tabs(self):
        roof = self.workflow.model.roof
        if self.roof_length_var is not None and roof:
            self.roof_length_var.set(f"{roof.length_m:.2f}"); self.roof_width_var.set(f"{roof.width_m:.2f}"); self.roof_dead_load_var.set(f"{roof.dead_load_kpa:.2f}"); self.roof_snow_load_var.set(f"{roof.snow_load_kpa:.2f}")
        level = self.active_level
        if self.envelope_finish_var is not None:
            self.envelope_finish_var.set(level.facade_finish); self.envelope_insulation_material_var.set(level.insulation_material); self.envelope_insulation_thickness_var.set(f"{level.insulation_thickness_m:.3f}"); self.envelope_plaster_material_var.set(level.interior_plaster_material); self.envelope_plaster_thickness_var.set(f"{level.interior_plaster_thickness_m:.3f}"); self.level_dead_load_var.set(f"{level.dead_load_kpa:.2f}"); self.level_live_load_var.set(f"{level.live_load_kpa:.2f}")
        self._refresh_structure_materials(); self._refresh_mep_tab()

    def refresh_view(self):
        super().refresh_view(); self._refresh_complete_tabs()

    def update_selected_wall(self):
        super().update_selected_wall()
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        if wall is not None and self.wall_load_bearing_var is not None:
            self.wall_load_bearing_var.set(wall.load_bearing); self.wall_tributary_var.set(f"{wall.tributary_width_m:.2f}")
            if wall.material_id in self.workflow.model.materials: self.wall_material_var.set(self.workflow.model.materials[wall.material_id].name)

    def apply_roof(self):
        try:
            roof = Roof(roof_type=self.roof_type_var.get().strip(), construction=self.roof_construction_var.get().strip(), covering=self.roof_covering_var.get().strip(), substructure=self.roof_substructure_var.get().strip(), support=self.roof_support_var.get().strip(), length_m=float(self.roof_length_var.get()), width_m=float(self.roof_width_var.get()), slope_deg=float(self.roof_slope_var.get()), height_m=float(self.roof_height_var.get()), dead_load_kpa=float(self.roof_dead_load_var.get()), snow_load_kpa=float(self.roof_snow_load_var.get()))
            self.workflow.model.set_roof(roof)
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Krov", str(exc), parent=self); return
        self.refresh_view(); self.status_var.set(f"Krov: {roof.length_m:.2f} × {roof.width_m:.2f} m")

    def _draw_facade(self):
        self.canvas.delete("all"); direction = self.facade_direction_var.get(); levels = list(self.workflow.model.levels.values()); horizontal = direction in {"Sjever", "Jug"}; max_span = max(((l.length_m if horizontal else l.width_m) for l in levels), default=10.0); width = max(self.canvas.winfo_width(), 700); height = max(self.canvas.winfo_height(), 450); scale = min(55.0, (width - 180) / max(max_span, 1.0)); base_y = height - 60; z = 0.0
        for level in levels:
            span = level.length_m if horizontal else level.width_m; x0 = (width - span * scale) / 2.0; x1 = x0 + span * scale; y0 = base_y - z * scale * 0.6; y1 = y0 - level.height * scale * 0.6
            self.canvas.create_rectangle(x0, y1, x1, y0, outline="#374151", width=3)
            for wall in (level.floor_plan.walls.values() if level.floor_plan else ()):
                aligned = abs(wall.segment.start.y - wall.segment.end.y) < 1e-6 if horizontal else abs(wall.segment.start.x - wall.segment.end.x) < 1e-6
                if not aligned: continue
                edge = level.width_m if direction == "Sjever" else 0.0 if direction == "Jug" else level.length_m if direction == "Istok" else 0.0; coord = wall.segment.start.y if horizontal else wall.segment.start.x
                if abs(coord - edge) > max(wall.thickness, 0.25): continue
                start = min(wall.segment.start.x, wall.segment.end.x) if horizontal else min(wall.segment.start.y, wall.segment.end.y); length = max(wall.segment.length, 1e-9)
                for opening in wall.openings:
                    ox0 = x0 + (start + opening.offset) * scale; ox1 = x0 + (start + opening.offset + opening.width) * scale; oy = y0 - opening.height_m * scale * 0.6; self.canvas.create_rectangle(ox0, oy, ox1, y0, fill="white", outline="#64748b")
            z += level.height
        self.canvas.create_text(20, 20, text=f"FASADA — {direction}", anchor="nw", font=("Segoe UI", 14, "bold"), fill="#1f2937")
        if self.workflow.model.roof: self.canvas.create_text(20, 45, text=f"Krov: {self.workflow.model.roof.length_m:.2f} × {self.workflow.model.roof.width_m:.2f} m", anchor="nw", fill="#475569")
        self.draw_compass()


def main() -> None:
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
