"""Complete LAT-CES desktop workspace with the canonical engineering navigation shell."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox, ttk

from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.mep_engineering import ensure_engineering_results
from lat_ces.building.model import Material
from lat_ces.building.structural import calculate_structural_loads
from lat_ces.gui import FloorPlanEditor
from lat_ces.gui_drafting import DraftingLATCESApp
from lat_ces.gui_mep_engineering import EngineeringMEPWorkspaceApp


class CompleteBuildingWorkspaceApp(DraftingLATCESApp):
    """One-window BuildingModel workspace with canonical LAT-CES navigation."""

    NAV_ITEMS = (
        ("OBJECT", "object"),
        ("MODEL", "model"),
        ("ANALYSIS", "analysis"),
        ("SYSTEMS", "systems"),
        ("ENERGY", "energy"),
        ("SERVICE", "service"),
        ("AI", "ai"),
    )

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
        self.current_nav = tk.StringVar(master=self, value="MODEL")
        self.current_context = tk.StringVar(master=self, value="BuildingModel")
        self._configure_engineering_style()
        self._install_canonical_shell()
        self._install_complete_tabs()
        self._refresh_complete_tabs()

    def _configure_engineering_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("LAT.TFrame", background="#f4f6f8")
        style.configure("LAT.Header.TFrame", background="#101820")
        style.configure("LAT.Nav.TFrame", background="#ffffff")
        style.configure("LAT.Title.TLabel", background="#101820", foreground="#ffffff", font=("Segoe UI", 18, "bold"))
        style.configure("LAT.Subtitle.TLabel", background="#101820", foreground="#b8c2cc", font=("Segoe UI", 9))
        style.configure("LAT.Nav.TButton", padding=(16, 10), font=("Segoe UI", 9, "bold"))
        style.configure("LAT.Card.TLabelframe", padding=10)
        style.configure("LAT.Card.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("LAT.Status.TLabel", background="#e9edf1", foreground="#334155", padding=(10, 6), font=("Segoe UI", 9))

    def _install_canonical_shell(self) -> None:
        shell = tk.Frame(self, bg="#f4f6f8")
        shell.pack(fill="both", expand=True, before=self.winfo_children()[0] if self.winfo_children() else None)

        header = ttk.Frame(shell, style="LAT.Header.TFrame")
        header.pack(fill="x")
        title_box = ttk.Frame(header, style="LAT.Header.TFrame")
        title_box.pack(side="left", padx=18, pady=14)
        ttk.Label(title_box, text="LAT-CES", style="LAT.Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Unified Building Engineering Workspace", style="LAT.Subtitle.TLabel").pack(anchor="w")
        ttk.Label(header, textvariable=self.current_context, style="LAT.Subtitle.TLabel").pack(side="right", padx=18, pady=14, anchor="s")

        nav = ttk.Frame(shell, style="LAT.Nav.TFrame")
        nav.pack(fill="x", padx=14, pady=(10, 0))
        self.nav_buttons = {}
        for label, key in self.NAV_ITEMS:
            btn = ttk.Button(nav, text=label, style="LAT.Nav.TButton", command=lambda k=key: self._select_nav(k))
            btn.pack(side="left", padx=2)
            self.nav_buttons[key] = btn

        context = tk.Frame(shell, bg="#f4f6f8")
        context.pack(fill="x", padx=18, pady=(8, 0))
        ttk.Label(context, text="ENGINEERING CONTEXT", font=("Segoe UI", 8, "bold"), foreground="#64748b").pack(side="left")
        ttk.Label(context, textvariable=self.current_nav, font=("Segoe UI", 10, "bold"), foreground="#0f172a").pack(side="left", padx=(8, 0))
        ttk.Label(context, text="  /  ", foreground="#94a3b8").pack(side="left")
        ttk.Label(context, textvariable=self.status_var, style="LAT.Status.TLabel").pack(side="right")

        self.shell_body = tk.Frame(shell, bg="#f4f6f8")
        self.shell_body.pack(fill="both", expand=True, padx=14, pady=(8, 0))

    def _select_nav(self, key: str) -> None:
        label = dict((k, v) for v, k in self.NAV_ITEMS).get(key, key.upper())
        self.current_nav.set(label)
        self.current_context.set({
            "object": "Building identity / Object definition",
            "model": "BuildingModel / Views / Envelope",
            "analysis": "Engineering analyses / Validation",
            "systems": "MEP / HVAC / Building systems",
            "energy": "Energy / Thermal / Solar",
            "service": "Reports / Quantities / Export",
            "ai": "Engineering Mentor / Explainability",
        }.get(key, "BuildingModel"))
        if key == "object":
            self._set_view_step(3)
        elif key == "model":
            self._set_view_step(3)
        elif key == "analysis":
            self._activate_complete_tab("calc")
        elif key == "systems":
            self._activate_complete_tab("mep")
        elif key == "energy":
            self._activate_complete_tab("envelope")
        elif key == "service":
            self._activate_complete_tab("calc")
        elif key == "ai":
            self._set_text(self.calculation_output, "Engineering Mentor / Explainability hooks are connected to the canonical BuildingModel workspace.\nNo engineering truth is duplicated in the GUI.")
            self._activate_complete_tab("calc")
        self.status_var.set(f"{label} aktivan")

    def _activate_complete_tab(self, key: str) -> None:
        if not hasattr(self, "complete_tabs"):
            return
        index = {"model": 0, "envelope": 1, "structure": 2, "calc": 3, "mep": 4, "facade": 5}.get(key, 0)
        self.complete_tabs.select(index)

    def _install_complete_tabs(self) -> None:
        children = list(self.winfo_children())
        old_steps = next((c for c in children if isinstance(c, ttk.Frame) and any(isinstance(x, ttk.Radiobutton) for x in c.winfo_children())), None)
        body = next((c for c in children if isinstance(c, ttk.Frame) and any(isinstance(x, ttk.LabelFrame) for x in c.winfo_children())), None)
        if old_steps is not None:
            old_steps.pack_forget()
        if body is None:
            return
        body.pack_forget()
        body.configure(style="LAT.TFrame")
        body.pack(in_=self.shell_body, fill="both", expand=True, padx=4, pady=4)
        self.complete_tabs = ttk.Notebook(body)
        self.complete_tabs.pack(fill="both", expand=True, padx=4, pady=4)
        self.complete_tabs.bind("<<NotebookTabChanged>>", lambda _e: self._refresh_complete_tabs())
        frames = {}
        for key, title in (("model", "Model / Pogledi"), ("envelope", "Omotač / Fasada"), ("structure", "Konstrukcija / Statika"), ("calc", "Proračuni"), ("mep", "MEP"), ("facade", "Fasade")):
            frame = ttk.Frame(self.complete_tabs, padding=12)
            self.complete_tabs.add(frame, text=title)
            frames[key] = frame
        self._build_model_tab(frames["model"])
        self._build_envelope_tab(frames["envelope"])
        self._build_structure_tab(frames["structure"])
        self._build_calc_tab(frames["calc"])
        self._build_mep_tab(frames["mep"])
        self._build_facade_tab(frames["facade"])

    def _build_model_tab(self, tab):
        top = ttk.LabelFrame(tab, text="OBJECT / MODEL — Pogledi i osnovni BuildingModel", style="LAT.Card.TLabelframe")
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Jedan fizički model, više inženjerskih pogleda.", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 8))
        actions = ttk.Frame(top)
        actions.pack(fill="x")
        for label, step in (("Krov", 1), ("Sprat", 2), ("Tlocrt", 3), ("Presjek", 4), ("3D", 5)):
            ttk.Button(actions, text=label, command=lambda s=step: self._set_view_step(s)).pack(side="left", padx=(0, 5))
        box = ttk.LabelFrame(tab, text="Krovna osnova i opterećenje", style="LAT.Card.TLabelframe")
        box.pack(fill="x")
        self.roof_length_var = tk.StringVar(value="10.00")
        self.roof_width_var = tk.StringVar(value="10.00")
        self.roof_dead_load_var = tk.StringVar(value="0.00")
        self.roof_snow_load_var = tk.StringVar(value="0.00")
        for label, var in (("Dužina (m)", self.roof_length_var), ("Širina (m)", self.roof_width_var), ("Stalno (kPa)", self.roof_dead_load_var), ("Snijeg (kPa)", self.roof_snow_load_var)):
            row = ttk.Frame(box)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=label, width=18).pack(side="left")
            ttk.Entry(row, textvariable=var, width=12).pack(side="left")
        ttk.Button(box, text="Primijeni krov", command=self.apply_roof).pack(anchor="w", pady=(6, 0))

    def _build_envelope_tab(self, tab):
        level = self.active_level
        self.envelope_finish_var = tk.StringVar(value=level.facade_finish)
        self.envelope_insulation_material_var = tk.StringVar(value=level.insulation_material)
        self.envelope_insulation_thickness_var = tk.StringVar(value=f"{level.insulation_thickness_m:.3f}")
        self.envelope_plaster_material_var = tk.StringVar(value=level.interior_plaster_material)
        self.envelope_plaster_thickness_var = tk.StringVar(value=f"{level.interior_plaster_thickness_m:.3f}")
        box = ttk.LabelFrame(tab, text="Omotač / Fasada", style="LAT.Card.TLabelframe")
        box.pack(fill="x")
        fields = (("Fasadna završna obrada", self.envelope_finish_var), ("Izolacija — materijal", self.envelope_insulation_material_var), ("Izolacija — debljina (m)", self.envelope_insulation_thickness_var), ("Unutrašnja žbuka — materijal", self.envelope_plaster_material_var), ("Unutrašnja žbuka — debljina (m)", self.envelope_plaster_thickness_var))
        for row, (label, var) in enumerate(fields):
            ttk.Label(box, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(box, textvariable=var, width=38).grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        ttk.Button(box, text="Primijeni slojeve omotača", command=self._apply_envelope).grid(row=5, column=0, columnspan=2, sticky="w", pady=8)
        box.columnconfigure(1, weight=1)

    def _build_structure_tab(self, tab):
        self.wall_load_bearing_var = tk.BooleanVar(value=False)
        self.wall_material_var = tk.StringVar(value="")
        self.wall_tributary_var = tk.StringVar(value="0.00")
        self.level_dead_load_var = tk.StringVar(value=f"{self.active_level.dead_load_kpa:.2f}")
        self.level_live_load_var = tk.StringVar(value=f"{self.active_level.live_load_kpa:.2f}")
        box = ttk.LabelFrame(tab, text="ANALYSIS — Konstrukcija / Statika", style="LAT.Card.TLabelframe")
        box.pack(fill="x")
        ttk.Checkbutton(box, text="Odabrani zid je NOSIV", variable=self.wall_load_bearing_var).grid(row=0, column=0, columnspan=2, sticky="w", pady=3)
        ttk.Label(box, text="Materijal").grid(row=1, column=0, sticky="w", pady=3)
        self.wall_material_combo = ttk.Combobox(box, textvariable=self.wall_material_var, state="readonly", width=30)
        self.wall_material_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=3)
        ttk.Label(box, text="Tributarna širina (m)").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(box, textvariable=self.wall_tributary_var).grid(row=2, column=1, sticky="ew", padx=8, pady=3)
        ttk.Button(box, text="Primijeni zid", command=self._apply_wall_structure).grid(row=3, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Separator(box).grid(row=4, column=0, columnspan=2, sticky="ew", pady=6)
        ttk.Label(box, text="Stalno q (kPa)").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Entry(box, textvariable=self.level_dead_load_var).grid(row=5, column=1, sticky="ew", padx=8, pady=3)
        ttk.Label(box, text="Korisno q (kPa)").grid(row=6, column=0, sticky="w", pady=3)
        ttk.Entry(box, textvariable=self.level_live_load_var).grid(row=6, column=1, sticky="ew", padx=8, pady=3)
        ttk.Button(box, text="Primijeni opterećenje etaže", command=self._apply_level_loads).grid(row=7, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Separator(box).grid(row=8, column=0, columnspan=2, sticky="ew", pady=6)
        self.material_name_var = tk.StringVar(value="Armirani beton")
        self.material_density_var = tk.StringVar(value="2500")
        self.material_e_var = tk.StringVar(value="30000000000")
        self.material_lambda_var = tk.StringVar(value="2.10")
        for row, (label, var) in enumerate((("Naziv", self.material_name_var), ("Gustina kg/m³", self.material_density_var), ("E Pa", self.material_e_var), ("λ W/mK", self.material_lambda_var)), start=9):
            ttk.Label(box, text=label).grid(row=row, column=0, sticky="w", pady=3)
            ttk.Entry(box, textvariable=var).grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        ttk.Button(box, text="Dodaj materijal", command=self._add_material).grid(row=13, column=0, columnspan=2, sticky="w", pady=6)
        box.columnconfigure(1, weight=1)

    def _build_calc_tab(self, tab):
        box = ttk.LabelFrame(tab, text="ANALYSIS / SERVICE — Inženjerski rezultati", style="LAT.Card.TLabelframe")
        box.pack(fill="both", expand=True)
        buttons = ttk.Frame(box)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Statika — preliminarna opterećenja", command=self._calculate_structure).pack(side="left", padx=(0, 5))
        ttk.Button(buttons, text="Building Engineering Report", command=self._calculate_building_report).pack(side="left", padx=(0, 5))
        ttk.Button(buttons, text="Provjeri model", command=self.validate_model).pack(side="left")
        self.calculation_output = tk.Text(box, height=14, wrap="word")
        self.calculation_output.pack(fill="both", expand=True, pady=8)
        self.calculation_output.configure(state="disabled")
        ttk.Label(box, text="Rezultati su izvedeni iz canonical BuildingModel-a; GUI nije izvor naučne istine.", foreground="#475569", wraplength=900).pack(fill="x")

    def _build_mep_tab(self, tab):
        box = ttk.LabelFrame(tab, text="SYSTEMS — MEP / HVAC", style="LAT.Card.TLabelframe")
        box.pack(fill="both", expand=True)
        actions = ttk.Frame(box)
        actions.pack(fill="x")
        ttk.Button(actions, text="Otvori MEP editor", command=self._open_mep_editor).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Izračunaj sve MEP", command=self._calculate_building_report).pack(side="left", padx=(0, 5))
        ttk.Button(actions, text="Osvježi", command=self._refresh_mep_tab).pack(side="left")
        self.mep_output = tk.Text(box, height=12, wrap="word")
        self.mep_output.pack(fill="both", expand=True, pady=8)
        self.mep_output.configure(state="disabled")

    def _build_facade_tab(self, tab):
        box = ttk.LabelFrame(tab, text="MODEL — Fasade", style="LAT.Card.TLabelframe")
        box.pack(fill="x")
        self.facade_direction_var = tk.StringVar(value="Sjever")
        ttk.Label(box, text="Smjer:").pack(side="left")
        ttk.Combobox(box, textvariable=self.facade_direction_var, state="readonly", values=("Sjever", "Istok", "Jug", "Zapad"), width=12).pack(side="left", padx=8)
        ttk.Button(box, text="Prikaži fasadu", command=self._draw_facade).pack(side="left")

    def _set_view_step(self, step):
        self.view_step.set(step)
        self.goto_step()

    def _apply_envelope(self):
        try:
            level = self.active_level
            level.facade_finish = self.envelope_finish_var.get().strip()
            level.insulation_material = self.envelope_insulation_material_var.get().strip()
            level.insulation_thickness_m = float(self.envelope_insulation_thickness_var.get())
            level.interior_plaster_material = self.envelope_plaster_material_var.get().strip()
            level.interior_plaster_thickness_m = float(self.envelope_plaster_thickness_var.get())
            if level.insulation_thickness_m < 0 or level.interior_plaster_thickness_m < 0:
                raise ValueError("Debljine slojeva ne mogu biti negativne")
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Omotač", str(exc), parent=self)
            return
        self.refresh_view()
        self.status_var.set("Omotač primijenjen")

    def _apply_level_loads(self):
        try:
            dead, live = float(self.level_dead_load_var.get()), float(self.level_live_load_var.get())
            if dead < 0 or live < 0:
                raise ValueError("Opterećenja ne mogu biti negativna")
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Statika", str(exc), parent=self)
            return
        self.active_level.dead_load_kpa = dead
        self.active_level.live_load_kpa = live
        self.status_var.set("Etažno opterećenje spremljeno")

    def _apply_wall_structure(self):
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        if wall is None:
            messagebox.showinfo("LAT-CES — Konstrukcija", "Prvo odaberi zid na tlocrtu.", parent=self)
            return
        try:
            tributary = float(self.wall_tributary_var.get())
            if tributary < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("LAT-CES — Konstrukcija", "Tributarna širina mora biti >= 0.", parent=self)
            return
        wall.load_bearing = bool(self.wall_load_bearing_var.get())
        name = self.wall_material_var.get().strip()
        wall.material_id = next((mid for mid, mat in self.workflow.model.materials.items() if mat.name == name), None)
        wall.tributary_width_m = tributary
        self.refresh_view()
        self.status_var.set(f"{wall.role_label}: {wall.name}")

    def _add_material(self):
        try:
            material = Material(
                name=self.material_name_var.get().strip(),
                density=float(self.material_density_var.get()),
                youngs_modulus=float(self.material_e_var.get()),
                thermal_conductivity=float(self.material_lambda_var.get()),
            )
            self.workflow.model.add_material(material)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Materijal", str(exc), parent=self)
            return
        self._refresh_structure_materials()
        self.status_var.set(f"Materijal dodat: {material.name}")

    def _refresh_structure_materials(self):
        if not hasattr(self, "wall_material_combo"):
            return
        names = [m.name for m in self.workflow.model.materials.values()]
        self.wall_material_combo["values"] = names
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        if wall and wall.material_id in self.workflow.model.materials:
            self.wall_material_var.set(self.workflow.model.materials[wall.material_id].name)
        elif not self.wall_material_var.get() and names:
            self.wall_material_var.set(names[0])

    def _calculate_structure(self):
        report = calculate_structural_loads(self.workflow.model)
        lines = [f"Status: {report.status}", f"Ukupno: {report.total_vertical_line_load_kn_m:.3f} kN/m"]
        if report.findings:
            lines += ["", "Nalazi:"] + [f"- {x}" for x in report.findings]
        lines += [f"{x.wall_name}: {x.line_load_kn_m:.3f} kN/m" for x in report.wall_results]
        self._set_text(self.calculation_output, "\n".join(lines))
        self.status_var.set("Statika izračunata")

    def _calculate_building_report(self):
        result = ensure_engineering_results(self.workflow.model)
        report = build_building_engineering_report(self.workflow.model)
        summary = [
            f"Building Engineering Report: {report.status}",
            f"Materijali: {report.material_count}",
            f"Etaže: {report.level_count}",
            f"MEP elementi: {report.mep_element_count}",
            f"Strukturno opterećenje: {result.structural_loads.total_vertical_line_load_kn_m:.3f} kN/m",
        ]
        self._set_text(self.calculation_output, "\n".join(summary))
        self._set_text(self.mep_output, "\n".join(result.mep_findings or ["MEP engineering registry OK"]))
        self.status_var.set("Building engineering rezultati osvježeni")

    @staticmethod
    def _set_text(widget, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _open_mep_editor(self):
        EngineeringMEPWorkspaceApp(self, self.workflow.model)

    def _draw_facade(self):
        self.view_step.set(4)
        self.goto_step()
        self.status_var.set(f"Fasada: {self.facade_direction_var.get()}")

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
        os._exit(0)
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
