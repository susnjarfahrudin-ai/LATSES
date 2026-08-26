"""Usable MEP engineering workspace UX over the canonical MEP model.

This wrapper keeps the existing MEP data/model implementation and room-zone
runtime, but fixes presentation and navigation problems found in the installed
Windows build.
"""
from __future__ import annotations

import copy
import tkinter as tk
from tkinter import messagebox, ttk

from lat_ces.building.mep import HEATING_EMITTERS, HEATING_SOURCES
from lat_ces.catalog.product_catalog import products_for_category
from lat_ces.gui_mep_system_workspace import EngineeringMEPWorkspaceApp as _BaseMEPWorkspace


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


class EngineeringMEPWorkspaceUXApp(_BaseMEPWorkspace):
    """MEP-only workspace with readable labels, navigation and scrollable controls."""

    def __init__(self) -> None:
        self._snapshot = None
        self._room_display_to_id: dict[str, str] = {}
        self._level_display_to_id: dict[str, str] = {}
        self._heating_room_display_to_id: dict[str, str] = {}
        self._ux_saved = False
        super().__init__()

    def set_workflow(self, workflow) -> None:
        self.workflow = workflow
        self._snapshot = copy.deepcopy(workflow)
        self._ux_saved = False
        self._refresh_context()
        self._draw_context()

    def refresh_view(self) -> None:
        if self.workflow is not None and self._snapshot is None:
            self._snapshot = copy.deepcopy(self.workflow)
        self._refresh_context()
        self._draw_context()

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(12, 8, 12, 4))
        header.pack(fill="x")
        ttk.Button(header, text="← Nazad", command=self._back_to_main).pack(side="left")
        ttk.Label(header, text="MEP ENGINEERING WORKSPACE", font=("Segoe UI", 15, "bold")).pack(side="left", padx=14)
        ttk.Label(header, text="BuildingModel: read-only fizički kontekst", foreground="#475569").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Sačuvaj izmjene na objektu", command=self._save_changes).pack(side="left", padx=2)
        ttk.Button(actions, text="Poništi izmjene", command=self._cancel_changes).pack(side="left", padx=2)

        body = ttk.Panedwindow(self, orient="horizontal")
        body.pack(fill="both", expand=True, padx=8, pady=(2, 8))
        context = ttk.Frame(body)
        main = ttk.Frame(body)
        body.add(context, weight=1)
        body.add(main, weight=5)
        self._build_context_ux(context)
        self._build_main_ux(main)

    def _build_context_ux(self, frame: ttk.Frame) -> None:
        ttk.Label(frame, text="BUILDING MODEL", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(2, 4))
        line = ttk.Separator(frame)
        line.pack(fill="x", pady=(0, 6))

        ttk.Label(frame, text="Etaža").pack(anchor="w")
        self.level_var = tk.StringVar(value="")
        self.level_combo = ttk.Combobox(frame, textvariable=self.level_var, state="readonly", width=30)
        self.level_combo.pack(fill="x", pady=(2, 8))
        self.level_combo.bind("<<ComboboxSelected>>", lambda _e: self._level_changed())

        ttk.Label(frame, text="Prostorija").pack(anchor="w")
        self.room_var = tk.StringVar(value="")
        self.room_combo = ttk.Combobox(frame, textvariable=self.room_var, state="readonly", width=30)
        self.room_combo.pack(fill="x", pady=(2, 8))
        self.room_combo.bind("<<ComboboxSelected>>", lambda _e: self._context_room_changed())

        self.context_text = tk.Text(frame, height=13, wrap="word", state="disabled", relief="flat", highlightthickness=1)
        self.context_text.pack(fill="both", expand=True)
        ttk.Separator(frame).pack(fill="x", pady=8)
        ttk.Label(
            frame,
            text="MEP čita Room/Level/Wall/Opening identitete iz BuildingModela. Ovdje se ne crtaju zidovi, krovovi ni prostorije.",
            wraplength=260,
            foreground="#475569",
        ).pack(fill="x")

    def _build_main_ux(self, frame: ttk.Frame) -> None:
        visual = ttk.Frame(frame)
        visual.pack(fill="both", expand=False)
        self.canvas = tk.Canvas(visual, height=390, background="white", relief="flat", highlightthickness=1, highlightbackground="#cbd5e1")
        self.canvas.pack(fill="both", expand=False)
        ttk.Separator(frame).pack(fill="x", pady=5)

        control_wrap = ttk.Frame(frame)
        control_wrap.pack(fill="both", expand=True)
        self.control_canvas = tk.Canvas(control_wrap, borderwidth=0, highlightthickness=0)
        self.control_scroll = ttk.Scrollbar(control_wrap, orient="vertical", command=self.control_canvas.yview)
        self.control_canvas.configure(yscrollcommand=self.control_scroll.set)
        self.control_scroll.pack(side="right", fill="y")
        self.control_canvas.pack(side="left", fill="both", expand=True)
        self.control_inner = ttk.Frame(self.control_canvas)
        self.control_window = self.control_canvas.create_window((0, 0), window=self.control_inner, anchor="nw")
        self.control_inner.bind("<Configure>", lambda _e: self.control_canvas.configure(scrollregion=self.control_canvas.bbox("all")))
        self.control_canvas.bind("<Configure>", lambda e: self.control_canvas.itemconfigure(self.control_window, width=e.width))
        self.control_canvas.bind_all("<MouseWheel>", self._scroll_controls)

        tabs = ttk.Notebook(self.control_inner)
        tabs.pack(fill="both", expand=True)
        self.tabs = tabs
        heating = ttk.Frame(tabs, padding=8)
        cooling = ttk.Frame(tabs, padding=8)
        ventilation = ttk.Frame(tabs, padding=8)
        water = ttk.Frame(tabs, padding=8)
        tabs.add(heating, text="Grijanje")
        tabs.add(cooling, text="Hlađenje")
        tabs.add(ventilation, text="Ventilacija")
        tabs.add(water, text="Voda")
        self._build_heating_ux(heating)
        self._build_cooling_tab(cooling)
        self._build_ventilation_tab(ventilation)
        self._build_water_tab(water)

    def _build_heating_ux(self, tab: ttk.Frame) -> None:
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

        top = ttk.Frame(tab); top.pack(fill="x")
        ttk.Label(top, text="ODABIR PROSTORIJE", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
        self.heating_room_combo = ttk.Combobox(top, textvariable=self.heating_room_var, state="readonly", width=34)
        self.heating_room_combo.grid(row=1, column=0, sticky="ew", pady=(2, 8))
        self.heating_room_combo.bind("<<ComboboxSelected>>", lambda _e: self._heating_room_changed())
        top.columnconfigure(0, weight=1)
        ttk.Separator(tab).pack(fill="x", pady=(2, 8))

        base = ttk.Frame(tab); base.pack(fill="x")
        left = ttk.Frame(base); left.pack(side="left", fill="y", padx=(0, 18))
        right = ttk.Frame(base); right.pack(side="left", fill="both", expand=True)

        self._form_combo_ux(left, "Izvor toplote", self.heating_source_var, HEATING_SOURCES, labels=_SOURCE_LABELS)
        self._form_combo_ux(left, "Predajnik", self.heating_emitter_var, HEATING_EMITTERS, labels=_EMITTER_LABELS)
        self._form_combo_ux(left, "Izvor — Product", self.source_product_var, "heating_products")
        self._form_combo_ux(left, "Predajnik — Product", self.emitter_product_var, "heating_products")
        self._field_ux(left, "Polaz (°C)", self.heating_supply_var)
        self._field_ux(left, "Povrat (°C)", self.heating_return_var)
        self._field_ux(left, "Cilj prostorije (°C)", self.heating_target_var)
        self._field_ux(left, "Projektno opterećenje (W)", self.heating_load_var)
        ttk.Button(left, text="＋ Dodaj / spremi zonu grijanja", command=self._save_heating_zone).pack(fill="x", pady=(8, 3))
        ttk.Button(left, text="Izračunaj odabranu MEP zonu", command=self._calculate_selected_heating).pack(fill="x")

        ttk.Label(right, text="PODNO GRIJANJE", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ufh = ttk.Frame(right); ufh.pack(fill="x", pady=(4, 0))
        self._form_combo_ux(ufh, "Cijev", self.underfloor_pipe_var, "underfloor_products")
        self._field_ux(ufh, "Razmak cijevi (m)", self.underfloor_spacing_var)
        self._form_combo_ux(ufh, "Izolacija", self.underfloor_insulation_var, "insulation_products")
        self._field_ux(ufh, "Izolacija — debljina (m)", self.underfloor_insulation_thickness_var)
        self._form_combo_ux(ufh, "Estrih", self.underfloor_screed_var, "screed_products")
        self._field_ux(ufh, "Estrih — debljina (m)", self.underfloor_screed_thickness_var)
        self._form_combo_ux(ufh, "Završni sloj", self.underfloor_finish_var, "finish_products")
        self._field_ux(ufh, "Završni sloj — debljina (m)", self.underfloor_finish_thickness_var)
        ttk.Button(right, text="＋ Dodaj / spremi podno grijanje", command=self._save_underfloor).pack(fill="x", pady=(8, 3))
        self.underfloor_status = tk.StringVar(value="Nije definisan podni sistem")
        ttk.Label(right, textvariable=self.underfloor_status, wraplength=850, foreground="#475569").pack(fill="x")

        self.heating_output = tk.Text(tab, height=7, wrap="word", state="disabled", relief="flat", highlightthickness=1)
        self.heating_output.pack(fill="both", expand=True, pady=(8, 0))

    def _form_combo_ux(self, parent, label, variable, values_key, labels=None) -> ttk.Combobox:
        row = ttk.Frame(parent); row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=28).pack(side="left")
        values = self._values_for_ux(values_key)
        display = [labels.get(v, v) for v in values] if labels else values
        combo = ttk.Combobox(row, textvariable=variable, state="readonly", values=display, width=34)
        combo.pack(side="left", fill="x", expand=True, padx=(7, 0))
        combo._lat_values = tuple(values)
        combo.bind("<<ComboboxSelected>>", lambda _e, c=combo: self._combo_selected_ux(c))
        if display and not variable.get():
            combo.current(0)
        return combo

    @staticmethod
    def _field_ux(parent, label, variable) -> None:
        row = ttk.Frame(parent); row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=28).pack(side="left")
        ttk.Entry(row, textvariable=variable, width=24).pack(side="left", fill="x", expand=True, padx=(7, 0))

    def _values_for_ux(self, key):
        if key == "heating_products":
            return tuple(p.product_id for p in products_for_category("Podno grijanje"))
        if key == "underfloor_products":
            return tuple(p.product_id for p in products_for_category("Podno grijanje"))
        if key == "insulation_products":
            return tuple(p.product_id for p in products_for_category("Izolacija"))
        if key == "screed_products":
            return tuple(p.product_id for p in products_for_category("Estrih"))
        if key == "finish_products":
            return tuple(p.product_id for p in products_for_category("Završni sloj"))
        return tuple(key) if isinstance(key, (tuple, list)) else ()

    def _combo_selected_ux(self, combo) -> None:
        values = getattr(combo, "_lat_values", ())
        if combo.current() >= 0 and combo.current() < len(values):
            combo.set(combo["values"][combo.current()])

    def _sync_level_and_room_labels(self) -> None:
        if self.workflow is None:
            return
        levels = list(self.workflow.model.levels.values())
        self._level_display_to_id = {level.name or f"Etaža {i+1}": level.level_id for i, level in enumerate(levels)}
        level_values = tuple(self._level_display_to_id.keys())
        self.level_combo["values"] = level_values
        selected_level_name = next((name for name, lid in self._level_display_to_id.items() if lid == self.active_level_id), None)
        if selected_level_name:
            self.level_var.set(selected_level_name)
        elif level_values:
            self.level_var.set(level_values[0]); self.active_level_id = self._level_display_to_id[level_values[0]]

        active = next((level for level in levels if level.level_id == self.active_level_id), None)
        if active is None:
            self.room_combo["values"] = ()
            self.heating_room_combo["values"] = ()
            return
        self._room_display_to_id = {room.name: room.room_id for room in active.rooms.values()}
        room_values = tuple(self._room_display_to_id.keys())
        self.room_combo["values"] = room_values
        self._heating_room_display_to_id = dict(self._room_display_to_id)
        self.heating_room_combo["values"] = room_values
        selected_name = next((name for name, rid in self._room_display_to_id.items() if rid == self.selected_room_id), None)
        if selected_name is None and room_values:
            selected_name = room_values[0]
            self.selected_room_id = self._room_display_to_id[selected_name]
        if selected_name:
            self.room_var.set(selected_name)
            self.heating_room_var.set(selected_name)

    def _refresh_context(self) -> None:
        if self.workflow is None:
            return
        self._sync_level_and_room_labels()
        active = next((level for level in self.workflow.model.levels.values() if level.level_id == self.active_level_id), None)
        if active is None:
            return
        wall_count = active.floor_plan.wall_count if active.floor_plan else 0
        opening_count = sum(len(wall.openings) for wall in active.floor_plan.walls.values()) if active.floor_plan else 0
        lines = [
            f"Etaža: {active.name}",
            f"Gabarit: {active.length_m:.2f} × {active.width_m:.2f} m",
            f"Visina: {active.height:.2f} m",
            f"Prostorije: {len(active.rooms)}",
            f"Zidovi: {wall_count}",
            f"Otvori: {opening_count}",
            "",
            f"Odabrana prostorija: {self._room_name(self.selected_room_id) if self.selected_room_id else 'Nije odabrana'}",
            "",
            "MEP ne mijenja građevinsku geometriju."
        ]
        self._set_text(self.context_text, "\n".join(lines))
        self._refresh_ventilation_and_water()

    def _level_changed(self) -> None:
        display = self.level_var.get()
        self.active_level_id = self._level_display_to_id.get(display)
        self.selected_room_id = None
        self._refresh_context()
        self._draw_context()

    def _context_room_changed(self) -> None:
        rid = self._room_display_to_id.get(self.room_var.get())
        self.selected_room_id = rid
        self.heating_room_var.set(self.room_var.get())
        self._refresh_context()
        self._draw_context()

    def _heating_room_changed(self) -> None:
        rid = self._heating_room_display_to_id.get(self.heating_room_var.get())
        self.selected_room_id = rid
        self.room_var.set(self.heating_room_var.get())
        self._refresh_context()
        self._draw_context()

    def _room_name(self, room_id: str | None) -> str:
        if not room_id or self.workflow is None:
            return room_id or ""
        for level in self.workflow.model.levels.values():
            room = level.rooms.get(room_id)
            if room is not None:
                return room.name
        return room_id

    def _save_changes(self) -> None:
        if self.workflow is None:
            return
        self._ux_saved = True
        self._snapshot = copy.deepcopy(self.workflow)
        self.status_var = getattr(self, "status_var", tk.StringVar(master=self, value=""))
        self.status_var.set("Izmjene su sačuvane u otvorenom BuildingModel objektu.")

    def _cancel_changes(self) -> None:
        if self.workflow is None or self._snapshot is None:
            self.destroy(); return
        restored = copy.deepcopy(self._snapshot)
        self.workflow.model = restored.model
        self.workflow.project_spec = restored.project_spec
        self.workflow.active_level_id = restored.active_level_id
        self.workflow.current_step = restored.current_step
        self._ux_saved = False
        self.destroy()

    def _back_to_main(self) -> None:
        self.destroy()

    def _scroll_controls(self, event) -> None:
        if event.delta:
            self.control_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _draw_context(self) -> None:
        # Keep the established MEP rendering implementation, but make the active
        # room visible and keep the selected floor plan in sync with the selector.
        super()._draw_context()
        if self.workflow is None or not self.selected_room_id:
            return
        active = next((level for level in self.workflow.model.levels.values() if level.level_id == self.active_level_id), None)
        if active is None or active.floor_plan is None:
            return
        room = active.rooms.get(self.selected_room_id)
        if room is None:
            return
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 390)
        margin = 40
        scale = min((width - 2 * margin) / max(active.length_m, 1.0), (height - 2 * margin) / max(active.width_m, 1.0))
        p, q = room.footprint.origin, room.footprint.max_point
        x1 = margin + p.x * scale; y1 = height - margin - p.y * scale
        x2 = margin + q.x * scale; y2 = height - margin - q.y * scale
        self.canvas.create_rectangle(x1 + 2, y2 + 2, x2 - 2, y1 - 2, outline="#0f766e", width=3)
        self.canvas.create_text((x1+x2)/2, y2-8, text=f"ODABRANO: {room.name}", fill="#0f766e", font=("Segoe UI", 9, "bold"))


# Preserve the public class name expected by the rest of LAT-CES.
EngineeringMEPWorkspaceApp = EngineeringMEPWorkspaceUXApp
