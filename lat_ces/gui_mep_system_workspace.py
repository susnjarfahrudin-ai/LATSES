"""MEP-only engineering workspace over the canonical BuildingModel.

The MEP workspace intentionally does not expose building drafting tools.  Rooms,
walls, openings and levels are read from the same BuildingModel; MEP objects are
stored in its canonical MEP registry.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from uuid import uuid4

from lat_ces.building.mep import HEATING_EMITTERS, HEATING_SOURCES, HeatingZone, ensure_mep_registry
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.catalog.product_catalog import products_for_category
from lat_ces.building.mep import UnderfloorHeatingSystem


_SOURCE_LABELS = {
    "heat_pump_air_water": "Toplotna pumpa zrak–voda",
    "heat_pump_air_air": "Toplotna pumpa zrak–zrak",
    "ground_source_heat_pump": "Geotermalna toplotna pumpa",
    "water_source_heat_pump": "Voda–voda toplotna pumpa",
    "gas_boiler": "Plinski kotao",
    "oil_boiler": "Uljni kotao",
    "pellet_boiler": "Pelet kotao",
    "pellet_stove": "Pelet peć",
    "wood_biomass_boiler": "Drvo / biomasa",
    "district_heating": "Daljinsko grijanje",
    "electric_boiler": "Električni kotao",
    "electric_direct": "Direktno električno grijanje",
    "infrared": "Infracrveno grijanje",
    "solar_thermal": "Solarno termalno",
    "hybrid": "Hibridno",
}

_EMITTER_LABELS = {
    "underfloor": "Podno grijanje",
    "radiator": "Radijatori",
    "fan_coil": "Fan-coil",
    "air_conditioner": "Klima / zrak–zrak",
    "wall_heating": "Zidno grijanje",
    "ceiling_heating": "Stropno grijanje",
    "convector": "Konvektor",
    "electric_panel": "Električni panel",
    "infrared_panel": "Infracrveni panel",
    "heated_towel_rail": "Kupaonski radijator",
    "air": "Zračno grijanje",
    "combined": "Kombinovano",
}


class EngineeringMEPWorkspaceApp(tk.Tk):
    """Standalone MEP environment; the BuildingModel is the physical context."""

    def __init__(self) -> None:
        super().__init__()
        self.title("LAT-CES — MEP Engineering Workspace")
        self.geometry("1480x920")
        self.minsize(1180, 760)
        self.workflow = None
        self.editor = None  # compatibility with the existing caller; never used for drafting
        self.active_level_id: str | None = None
        self.selected_room_id: str | None = None
        self._build_ui()

    # Compatibility hooks used by the current CompleteBuildingWorkspaceApp.
    def refresh_view(self) -> None:
        self._refresh_context()
        self._draw_context()

    def configure_stage(self, _step: int) -> None:
        return

    def set_workflow(self, workflow) -> None:
        self.workflow = workflow
        self._refresh_context()
        self._draw_context()

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(14, 12, 14, 6))
        header.pack(fill="x")
        ttk.Label(header, text="MEP ENGINEERING WORKSPACE", font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Label(
            header,
            text="BuildingModel je fizički source of truth · ovaj prostor ne crta zidove, krovove ni prostorije",
            foreground="#475569",
        ).pack(side="left", padx=18)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=12, pady=(4, 12))

        context = ttk.Frame(body, padding=8)
        main = ttk.Frame(body, padding=8)
        body.add(context, weight=1)
        body.add(main, weight=4)

        self._build_context(context)
        self._build_main(main)

    def _build_context(self, frame: ttk.Frame) -> None:
        context_box = ttk.LabelFrame(frame, text="BuildingModel — read-only kontekst", padding=10)
        context_box.pack(fill="x")
        self.level_var = tk.StringVar(value="")
        self.room_var = tk.StringVar(value="")
        ttk.Label(context_box, text="Etaža").grid(row=0, column=0, sticky="w", pady=3)
        self.level_combo = ttk.Combobox(context_box, textvariable=self.level_var, state="readonly", width=26)
        self.level_combo.grid(row=0, column=1, sticky="ew", padx=8, pady=3)
        self.level_combo.bind("<<ComboboxSelected>>", lambda _e: self._level_changed())
        ttk.Label(context_box, text="Prostorija").grid(row=1, column=0, sticky="w", pady=3)
        self.room_combo = ttk.Combobox(context_box, textvariable=self.room_var, state="readonly", width=26)
        self.room_combo.grid(row=1, column=1, sticky="ew", padx=8, pady=3)
        self.room_combo.bind("<<ComboboxSelected>>", lambda _e: self._room_changed())
        self.context_text = tk.Text(context_box, height=15, wrap="word", state="disabled")
        self.context_text.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        context_box.columnconfigure(1, weight=1)

        rule = ttk.LabelFrame(frame, text="Ustavno pravilo", padding=10)
        rule.pack(fill="x", pady=(10, 0))
        ttk.Label(
            rule,
            text="MEP koristi Room/Level/Wall/Opening identitete iz BuildingModela. Ne pravi novu geometrijsku kuću.",
            wraplength=320,
            foreground="#334155",
        ).pack(fill="x")

    def _build_main(self, frame: ttk.Frame) -> None:
        top = ttk.Frame(frame)
        top.pack(fill="both", expand=True)

        visual_box = ttk.LabelFrame(top, text="Vizuelni kontekst — read-only", padding=6)
        visual_box.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(visual_box, background="white", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas.pack(fill="both", expand=True)

        tabs = ttk.Notebook(top)
        tabs.pack(fill="x", pady=(8, 0))
        self.tabs = tabs
        heating = ttk.Frame(tabs, padding=10)
        cooling = ttk.Frame(tabs, padding=10)
        ventilation = ttk.Frame(tabs, padding=10)
        water = ttk.Frame(tabs, padding=10)
        tabs.add(heating, text="Grijanje")
        tabs.add(cooling, text="Hlađenje")
        tabs.add(ventilation, text="Ventilacija")
        tabs.add(water, text="Voda")
        self._build_heating_tab(heating)
        self._build_cooling_tab(cooling)
        self._build_ventilation_tab(ventilation)
        self._build_water_tab(water)

    def _build_heating_tab(self, tab: ttk.Frame) -> None:
        self.heating_room_var = tk.StringVar(value="")
        self.heating_source_var = tk.StringVar(value="heat_pump_air_water")
        self.heating_emitter_var = tk.StringVar(value="underfloor")
        self.heating_supply_var = tk.StringVar(value="35.0")
        self.heating_return_var = tk.StringVar(value="30.0")
        self.heating_target_var = tk.StringVar(value="20.0")
        self.heating_load_var = tk.StringVar(value="")
        self.underfloor_pipe_var = tk.StringVar(value="UFH-PEX-16X2")
        self.underfloor_spacing_var = tk.StringVar(value="0.15")
        self.underfloor_insulation_var = tk.StringVar(value="INSULATION-EPS")
        self.underfloor_insulation_thickness_var = tk.StringVar(value="0.05")
        self.underfloor_screed_var = tk.StringVar(value="")
        self.underfloor_screed_thickness_var = tk.StringVar(value="0.05")
        self.underfloor_finish_var = tk.StringVar(value="")
        self.underfloor_finish_thickness_var = tk.StringVar(value="0.01")
        self.source_product_var = tk.StringVar(value="")
        self.emitter_product_var = tk.StringVar(value="")

        left = ttk.Frame(tab); left.pack(side="left", fill="y", padx=(0, 18))
        right = ttk.Frame(tab); right.pack(side="left", fill="both", expand=True)

        self._form_combo(left, "Prostorija", self.heating_room_var, "rooms", 0)
        self._form_combo(left, "Izvor toplote", self.heating_source_var, HEATING_SOURCES, 1, labels=_SOURCE_LABELS)
        self._form_combo(left, "Predajnik", self.heating_emitter_var, HEATING_EMITTERS, 2, labels=_EMITTER_LABELS)
        self._form_combo(left, "Izvor — Product ID", self.source_product_var, "heating_products", 3)
        self._form_combo(left, "Predajnik — Product ID", self.emitter_product_var, "heating_products", 4)
        self._field(left, "Polaz (°C)", self.heating_supply_var, 5)
        self._field(left, "Povrat (°C)", self.heating_return_var, 6)
        self._field(left, "Cilj prostorije (°C)", self.heating_target_var, 7)
        self._field(left, "Projektno opterećenje (W)", self.heating_load_var, 8)
        ttk.Button(left, text="＋ Dodaj / spremi zonu grijanja", command=self._save_heating_zone).grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 3))
        ttk.Button(left, text="Izračunaj odabranu MEP zonu", command=self._calculate_selected_heating).grid(row=10, column=0, columnspan=2, sticky="ew")

        ufh = ttk.LabelFrame(right, text="Podno grijanje — konfiguracija poda i mreže", padding=10)
        ufh.pack(fill="x")
        self._form_combo(ufh, "Cijev", self.underfloor_pipe_var, "underfloor_products", 0)
        self._field(ufh, "Razmak cijevi (m)", self.underfloor_spacing_var, 1)
        self._form_combo(ufh, "Izolacija", self.underfloor_insulation_var, "insulation_products", 2)
        self._field(ufh, "Izolacija — debljina (m)", self.underfloor_insulation_thickness_var, 3)
        self._form_combo(ufh, "Estrih", self.underfloor_screed_var, "", 4)
        self._field(ufh, "Estrih — debljina (m)", self.underfloor_screed_thickness_var, 5)
        self._form_combo(ufh, "Završni sloj", self.underfloor_finish_var, "", 6)
        self._field(ufh, "Završni sloj — debljina (m)", self.underfloor_finish_thickness_var, 7)
        ttk.Button(ufh, text="＋ Dodaj / spremi podno grijanje", command=self._save_underfloor).grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8, 3))
        self.underfloor_status = tk.StringVar(value="Nije definisan podni sistem")
        ttk.Label(ufh, textvariable=self.underfloor_status, wraplength=650).grid(row=9, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.heating_output = tk.Text(right, height=8, wrap="word", state="disabled")
        self.heating_output.pack(fill="both", expand=True, pady=(8, 0))

    def _build_cooling_tab(self, tab: ttk.Frame) -> None:
        ttk.Label(tab, text="Hlađenje", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(
            tab,
            text="Hlađenje je zaseban MEP domen. Ovaj workspace ga već izdvaja od građevinskog modela; canonical CoolingSystem contract slijedi prije računanja.",
            wraplength=800,
            foreground="#475569",
        ).pack(anchor="w", pady=(6, 12))
        options = ("klima / zrak–zrak", "fan-coil", "stropno", "zidno", "podno površinsko hlađenje", "hibridno")
        ttk.Label(tab, text="Predloženi predajnici").pack(anchor="w")
        for option in options:
            ttk.Label(tab, text=f"• {option}").pack(anchor="w")
        ttk.Label(tab, text="Status: MODEL_CONTRACT_PENDING — nema izmišljenog engineering rezultata.", foreground="#92400e").pack(anchor="w", pady=(10, 0))

    def _build_ventilation_tab(self, tab: ttk.Frame) -> None:
        ttk.Label(tab, text="Ventilacija", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.ventilation_text = tk.Text(tab, height=9, wrap="word", state="disabled")
        self.ventilation_text.pack(fill="both", expand=True, pady=8)
        ttk.Label(tab, text="Ventilacioni Product ID može se vezati za postojeći VentilationOpening bez kopiranja prostora ili zida.", foreground="#475569").pack(anchor="w")

    def _build_water_tab(self, tab: ttk.Frame) -> None:
        ttk.Label(tab, text="Voda", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.water_text = tk.Text(tab, height=9, wrap="word", state="disabled")
        self.water_text.pack(fill="both", expand=True, pady=8)
        ttk.Label(tab, text="Voda čita postojeće WaterBranch objekte; novi hidraulički solver dolazi nakon canonical input contracta.", foreground="#475569").pack(anchor="w")

    @staticmethod
    def _field(parent, label: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        ttk.Entry(parent, textvariable=variable, width=28).grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        parent.columnconfigure(1, weight=1)

    def _form_combo(self, parent, label, variable, values_key, row, labels=None) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        values = self._values_for(values_key)
        display = [labels.get(v, v) for v in values] if labels else values
        combo = ttk.Combobox(parent, textvariable=variable, state="readonly", values=display, width=28)
        combo.grid(row=row, column=1, sticky="ew", padx=8, pady=3)
        self._combo_maps[id(combo)] = (values, display, variable)
        combo.bind("<<ComboboxSelected>>", lambda _e, c=combo, lbl=labels: self._combo_selected(c, lbl))
        if display and not variable.get():
            variable.set(display[0] if labels else values[0])

    def _combo_selected(self, combo, labels) -> None:
        values, display, variable = self._combo_maps[id(combo)]
        index = combo.current()
        if index >= 0:
            variable.set(values[index])

    def _values_for(self, key):
        if not hasattr(self, "_combo_maps"):
            self._combo_maps = {}
        if key == "rooms":
            if self.workflow is None:
                return ()
            return tuple(room.room_id for level in self.workflow.model.levels.values() for room in level.rooms.values())
        if key == "heating_products":
            return tuple(p.product_id for p in products_for_category("Podno grijanje"))
        if key == "underfloor_products":
            return tuple(p.product_id for p in products_for_category("Podno grijanje"))
        if key == "insulation_products":
            return tuple(p.product_id for p in products_for_category("Izolacija"))
        return tuple(key) if isinstance(key, (tuple, list)) else ()

    def _room_name(self, room_id: str) -> str:
        if self.workflow is None:
            return room_id
        for level in self.workflow.model.levels.values():
            room = level.rooms.get(room_id)
            if room is not None:
                return room.name
        return room_id

    def _level_changed(self) -> None:
        value = self.level_var.get()
        self.active_level_id = value.split(" ")[0] if value else None
        self._refresh_context()
        self._draw_context()

    def _room_changed(self) -> None:
        self.selected_room_id = self.room_var.get().split(" ")[0] if self.room_var.get() else None
        self._refresh_context()

    def _refresh_context(self) -> None:
        if self.workflow is None:
            return
        levels = list(self.workflow.model.levels.values())
        level_display = [f"{level.level_id} · {level.name}" for level in levels]
        self.level_combo["values"] = level_display
        if level_display and not self.level_var.get():
            self.level_var.set(level_display[0])
            self.active_level_id = levels[0].level_id
        active = next((level for level in levels if level.level_id == self.active_level_id), levels[0] if levels else None)
        if active is None:
            return
        room_values = [f"{room.room_id} · {room.name}" for room in active.rooms.values()]
        self.room_combo["values"] = room_values
        if room_values and not self.room_var.get():
            self.room_var.set(room_values[0])
            self.selected_room_id = active.rooms[next(iter(active.rooms))].room_id
        lines = [
            f"Level: {active.name}",
            f"Gabarit: {active.length_m:.2f} × {active.width_m:.2f} m",
            f"Visina: {active.height:.2f} m",
            f"Prostorije: {len(active.rooms)}",
            f"Zidovi: {active.floor_plan.wall_count if active.floor_plan else 0}",
            f"Otvoreni: {sum(len(wall.openings) for wall in active.floor_plan.walls.values()) if active.floor_plan else 0}",
            "",
            "Ovaj panel je samo kontekst. Geometrija se ne uređuje u MEP-u.",
        ]
        self._set_text(self.context_text, "\n".join(lines))
        self._refresh_ventilation_and_water()
        self._refresh_heating_controls()

    def _refresh_heating_controls(self) -> None:
        if self.workflow is None:
            return
        # Room selector is already rebuilt from the active level; keep canonical ids in forms.
        for child in self.tabs.winfo_children():
            # No-op; widgets are updated lazily from the selected model objects.
            _ = child

    def _refresh_ventilation_and_water(self) -> None:
        if self.workflow is None:
            return
        registry = ensure_mep_registry(self.workflow.model)
        vent_lines = [
            f"{o.id} · {o.room_id} · {o.kind} · Ø{o.diameter_m:.3f} m · {o.design_flow_m3_h:.1f} m³/h"
            for o in registry.all_ventilation_openings
        ] or ["Nema ventilacionih otvora u canonical MEP registry-ju."]
        water_lines = [
            f"{b.id} · {b.room_id} · {b.service} · Ø{b.diameter_m:.3f} m · {b.design_flow_m3_s:.5f} m³/s"
            for b in registry.all_water_branches
        ] or ["Nema vodnih grana u canonical MEP registry-ju."]
        self._set_text(self.ventilation_text, "\n".join(vent_lines))
        self._set_text(self.water_text, "\n".join(water_lines))

    def _save_heating_zone(self) -> None:
        if self.workflow is None or not self.room_var.get():
            messagebox.showwarning("LAT-CES — Grijanje", "Učitaj BuildingModel i izaberi prostoriju.", parent=self)
            return
        try:
            supply = float(self.heating_supply_var.get())
            return_temp = float(self.heating_return_var.get())
            target = float(self.heating_target_var.get())
            load = self.heating_load_var.get().strip()
            load_w = float(load) if load else None
            room_id = self.selected_room_id or self.room_var.get().split(" ")[0]
            if supply <= return_temp:
                raise ValueError("Polazna temperatura mora biti viša od povratne")
            zone = HeatingZone(
                id=f"HZ-{uuid4().hex[:8].upper()}",
                room_id=room_id,
                emitter_type=self.heating_emitter_var.get(),
                design_supply_temp_c=supply,
                design_return_temp_c=return_temp,
                target_indoor_temp_c=target,
                room_heat_load_w=load_w,
                source_type=self.heating_source_var.get(),
                source_product_id=self.source_product_var.get().strip() or None,
                emitter_product_id=self.emitter_product_var.get().strip() or None,
            )
            ensure_mep_registry(self.workflow.model).add_heating_zone(zone)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Grijanje", str(exc), parent=self)
            return
        self._set_text(self.heating_output, f"Spremljeno: {zone.id}\nProstorija: {self._room_name(zone.room_id)}\nIzvor: {_SOURCE_LABELS.get(zone.source_type, zone.source_type)}\nPredajnik: {_EMITTER_LABELS.get(zone.emitter_type, zone.emitter_type)}\nPolaz/povrat: {zone.design_supply_temp_c:.1f}/{zone.design_return_temp_c:.1f} °C")
        self.refresh_view()

    def _save_underfloor(self) -> None:
        if self.workflow is None or not self.selected_room_id:
            messagebox.showwarning("LAT-CES — Podno grijanje", "Izaberi prostoriju.", parent=self)
            return
        try:
            spacing = float(self.underfloor_spacing_var.get())
            insulation_thickness = float(self.underfloor_insulation_thickness_var.get())
            screed_thickness = float(self.underfloor_screed_thickness_var.get())
            finish_thickness = float(self.underfloor_finish_thickness_var.get())
            if spacing <= 0:
                raise ValueError("Razmak cijevi mora biti > 0")
            system = UnderfloorHeatingSystem(
                id=f"UFH-{uuid4().hex[:8].upper()}",
                room_id=self.selected_room_id,
                level_id=self.active_level_id or "",
                pipe_product_id=self.underfloor_pipe_var.get(),
                pipe_spacing_m=spacing,
                insulation_product_id=self.underfloor_insulation_var.get() or None,
                insulation_thickness_m=insulation_thickness,
                screed_product_id=self.underfloor_screed_var.get() or None,
                screed_thickness_m=screed_thickness,
                finish_product_id=self.underfloor_finish_var.get() or None,
                finish_thickness_m=finish_thickness,
                source_type=self.heating_source_var.get(),
                source_product_id=self.source_product_var.get().strip() or None,
                target_indoor_temp_c=float(self.heating_target_var.get()),
                design_supply_temp_c=float(self.heating_supply_var.get()),
                design_return_temp_c=float(self.heating_return_var.get()),
            )
            ensure_mep_registry(self.workflow.model).add_underfloor_system(system)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Podno grijanje", str(exc), parent=self)
            return
        self.underfloor_status.set(
            f"{system.id} · {self._room_name(system.room_id)} · cijev {system.pipe_product_id} · razmak {system.pipe_spacing_m:.3f} m · izolacija {system.insulation_thickness_m:.3f} m · estrih {system.screed_thickness_m:.3f} m · završni sloj {system.finish_thickness_m:.3f} m"
        )
        self.refresh_view()

    def _calculate_selected_heating(self) -> None:
        if self.workflow is None or not self.selected_room_id:
            return
        registry = ensure_mep_registry(self.workflow.model)
        zones = [zone for zone in registry.all_heating_zones if zone.room_id == self.selected_room_id]
        if not zones:
            self._set_text(self.heating_output, "Nema zone grijanja za odabranu prostoriju.")
            return
        zone = zones[-1]
        if zone.room_heat_load_w is None:
            self._set_text(self.heating_output, "INPUT_REQUIRED\nZa proračun treba projektno toplotno opterećenje iz Termike/BuildingModela.")
            return
        self._set_text(self.heating_output, f"CALCULATED\nZona: {zone.id}\nToplotno opterećenje: {zone.room_heat_load_w:.2f} W\nSpecifično opterećenje se računa tek nakon potvrđenih površina i termičkog modela.")

    def _draw_context(self) -> None:
        self.canvas.delete("all")
        if self.workflow is None:
            self.canvas.create_text(30, 30, anchor="nw", text="BuildingModel nije učitan.", fill="#475569", font=("Segoe UI", 12, "bold"))
            return
        levels = list(self.workflow.model.levels.values())
        active = next((level for level in levels if level.level_id == self.active_level_id), levels[0] if levels else None)
        if active is None or active.floor_plan is None:
            return
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 420)
        margin = 40
        scale = min((width - 2 * margin) / max(active.length_m, 1.0), (height - 2 * margin) / max(active.width_m, 1.0))
        def xy(x, y):
            return margin + x * scale, height - margin - y * scale
        for wall in active.floor_plan.walls.values():
            x1, y1 = xy(wall.segment.start.x, wall.segment.start.y)
            x2, y2 = xy(wall.segment.end.x, wall.segment.end.y)
            self.canvas.create_line(x1, y1, x2, y2, fill="#334155", width=5)
        for room in active.rooms.values():
            p, q = room.footprint.origin, room.footprint.max_point
            x1, y1 = xy(p.x, p.y)
            x2, y2 = xy(q.x, q.y)
            self.canvas.create_rectangle(x1, y2, x2, y1, outline="#94a3b8", dash=(3, 3))
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=room.name, fill="#475569")
        registry = ensure_mep_registry(self.workflow.model)
        for zone in registry.all_heating_zones:
            if zone.room_id in active.rooms:
                room = active.rooms[zone.room_id]
                p, q = room.footprint.origin, room.footprint.max_point
                x1, y1 = xy(p.x, p.y); x2, y2 = xy(q.x, q.y)
                self.canvas.create_rectangle(x1 + 4, y2 + 4, x2 - 4, y1 - 4, outline="#dc2626", width=3, dash=(7, 4))
        for system in registry.all_underfloor_systems:
            if system.level_id != active.level_id:
                continue
            room = active.rooms.get(system.room_id)
            if room is None:
                continue
            p, q = room.footprint.origin, room.footprint.max_point
            x1, y1 = xy(p.x, p.y); x2, y2 = xy(q.x, q.y)
            spacing_px = max(6.0, system.pipe_spacing_m * scale)
            y = y2 + 6
            while y < y1 - 6:
                self.canvas.create_line(x1 + 7, y, x2 - 7, y, fill="#2563eb", width=1, tags="ufh-schematic")
                y += spacing_px
        self.canvas.create_text(margin, margin - 10, anchor="sw", text=f"MEP KONTEKST · {active.name}", font=("Segoe UI", 13, "bold"), fill="#1f2937")

    @staticmethod
    def _set_text(widget: tk.Text, value: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", value)
        widget.configure(state="disabled")


def main() -> None:
    EngineeringMEPWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
