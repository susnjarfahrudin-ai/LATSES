"""Runtime behavior for the readable MEP workspace."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from uuid import uuid4

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_zones import UnderfloorZone, ZONE_MODES

ZONE_LABELS = {"full": "Cijela prostorija", "half_a": "1/2 — A", "half_b": "1/2 — B"}


def install(cls):
    original_init = cls.__init__
    original_save_underfloor = cls._save_underfloor
    original_draw = cls._draw_context

    def _form_combo_ux(self, parent, label, variable, values_key, labels=None):
        row = ttk.Frame(parent); row.pack(fill="x", pady=2)
        ttk.Label(row, text=label, width=28).pack(side="left")
        values = self._values_for_ux(values_key)
        display = [labels.get(v, v) for v in values] if labels else list(values)
        combo = ttk.Combobox(row, textvariable=variable, state="readonly", values=display, width=34)
        combo.pack(side="left", fill="x", expand=True, padx=(7, 0))
        combo._lat_values = tuple(values)
        combo._lat_variable = variable
        combo.bind("<<ComboboxSelected>>", lambda _e, c=combo: self._combo_selected_ux(c))
        if values:
            current = variable.get()
            index = list(values).index(current) if current in values else 0
            combo.current(index)
        return combo

    def __init__(self, *args, **kwargs):
        self._form_combo_ux = _form_combo_ux.__get__(self, cls)
        original_init(self, *args, **kwargs)
        self.zone_mode_var = tk.StringVar(master=self, value=ZONE_LABELS["full"])
        box = self.tabs.nametowidget(self.tabs.tabs()[0])
        zone = ttk.Frame(box)
        zone.pack(fill="x", pady=(5, 0))
        ttk.Label(zone, text="Podna zona").pack(side="left")
        ttk.Combobox(zone, textvariable=self.zone_mode_var, state="readonly", values=tuple(ZONE_LABELS[m] for m in ZONE_MODES), width=24).pack(side="left", padx=(8, 0))
        ttk.Label(zone, text="Cijela ili 1/2 A/B · za veće prostorije mogu se koristiti dvije nezavisne zone.", foreground="#475569").pack(side="left", padx=10)

    def _combo_selected_ux(self, combo):
        values = tuple(getattr(combo, "_lat_values", ()))
        variable = getattr(combo, "_lat_variable", None)
        index = combo.current()
        if variable is not None and 0 <= index < len(values):
            variable.set(values[index])

    def _save_underfloor(self):
        original_save_underfloor(self)
        if self.workflow is None or not self.selected_room_id:
            return
        registry = ensure_mep_registry(self.workflow.model)
        systems = [s for s in registry.all_underfloor_systems if s.room_id == self.selected_room_id]
        if not systems:
            return
        system = systems[-1]
        mode = next((key for key, value in ZONE_LABELS.items() if value == self.zone_mode_var.get()), "full")
        zones = getattr(registry, "underfloor_zones", None)
        if zones is None:
            zones = {}
            setattr(registry, "underfloor_zones", zones)
        zone = UnderfloorZone(id=f"UFZ-{uuid4().hex[:8].upper()}", system_id=system.id, room_id=system.room_id, level_id=system.level_id, mode=mode)
        zones[zone.id] = zone
        self.underfloor_status.set(f"{self.underfloor_status.get()} · zona: {zone.label}")
        self._draw_context()

    def _draw_context(self):
        registry = ensure_mep_registry(self.workflow.model) if self.workflow is not None else None
        if registry is None:
            original_draw(self)
            return
        saved_systems = registry.underfloor_systems
        registry.underfloor_systems = {}
        try:
            original_draw(self)
        finally:
            registry.underfloor_systems = saved_systems
        levels = list(self.workflow.model.levels.values())
        active = next((l for l in levels if l.level_id == self.active_level_id), None)
        if active is None or active.floor_plan is None:
            return
        width = max(self.canvas.winfo_width(), 700)
        height = max(self.canvas.winfo_height(), 390)
        margin = 40
        scale = min((width - 2 * margin) / max(active.length_m, 1.0), (height - 2 * margin) / max(active.width_m, 1.0))
        def xy(x, y):
            return margin + x * scale, height - margin - y * scale
        zones = getattr(registry, "underfloor_zones", {})
        for system in registry.all_underfloor_systems:
            if system.level_id != active.level_id:
                continue
            room = active.rooms.get(system.room_id)
            if room is None:
                continue
            room_zones = [z for z in zones.values() if z.system_id == system.id]
            if not room_zones:
                room_zones = [UnderfloorZone(id="TEMP", system_id=system.id, room_id=system.room_id, level_id=system.level_id)]
            p, q = room.footprint.origin, room.footprint.max_point
            for zone in room_zones:
                left, right = p.x, q.x
                if zone.mode == "half_a":
                    right = p.x + (q.x - p.x) / 2.0
                elif zone.mode == "half_b":
                    left = p.x + (q.x - p.x) / 2.0
                x1, y1 = xy(left, p.y); x2, y2 = xy(right, q.y)
                self.canvas.create_rectangle(x1 + 4, y2 + 4, x2 - 4, y1 - 4, outline="#1d4ed8", width=2, dash=(5, 3))
                spacing_px = max(6.0, system.pipe_spacing_m * scale)
                y = y2 + 8
                while y < y1 - 8:
                    self.canvas.create_line(x1 + 8, y, x2 - 8, y, fill="#2563eb", width=1)
                    y += spacing_px
                self.canvas.create_text((x1 + x2) / 2, y2 + 12, text=f"Podno · {zone.label}", fill="#1d4ed8", font=("Segoe UI", 9, "bold"))

    cls.__init__ = __init__
    cls._form_combo_ux = _form_combo_ux
    cls._combo_selected_ux = _combo_selected_ux
    cls._save_underfloor = _save_underfloor
    cls._draw_context = _draw_context
    return cls
