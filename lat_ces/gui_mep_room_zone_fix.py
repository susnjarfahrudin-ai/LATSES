"""Runtime adapter for synchronized MEP room selection and underfloor zones."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from uuid import uuid4

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.mep_zones import UnderfloorZone, ZONE_MODES

_ZONE_LABELS = {"full": "Cijela prostorija", "half_a": "1/2 — A", "half_b": "1/2 — B"}


def _heating_room_combo(app):
    target = str(app.heating_room_var)
    heating_tab = app.tabs.nametowidget(app.tabs.tabs()[0])
    for child in heating_tab.winfo_children():
        for widget in child.winfo_children() if isinstance(child, (ttk.Frame, ttk.LabelFrame)) else ():
            if isinstance(widget, ttk.Combobox) and widget.cget("textvariable") == target:
                return widget
    return None


def install_room_zone_behavior(cls):
    original_init = cls.__init__
    original_refresh_context = cls._refresh_context
    original_room_changed = cls._room_changed
    original_level_changed = cls._level_changed
    original_combo_selected = cls._combo_selected
    original_save_underfloor = cls._save_underfloor
    original_draw_context = cls._draw_context

    def _init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        self.zone_mode_var = tk.StringVar(master=self, value=_ZONE_LABELS["full"])
        heating_tab = self.tabs.nametowidget(self.tabs.tabs()[0])
        zone_box = ttk.LabelFrame(heating_tab, text="Podna zona", padding=8)
        zone_box.pack(fill="x", pady=(8, 0))
        self.zone_mode_combo = ttk.Combobox(zone_box, textvariable=self.zone_mode_var, state="readonly", values=tuple(_ZONE_LABELS[m] for m in ZONE_MODES), width=24)
        self.zone_mode_combo.pack(side="left")
        ttk.Label(zone_box, text="Za veće prostorije: cijela ili 1/2 A/B. Dvije zone mogu pokriti obje polovine iste prostorije.", foreground="#475569", wraplength=620).pack(side="left", padx=10)

    def _sync_room_controls(self):
        if self.workflow is None:
            return
        level = next((x for x in self.workflow.model.levels.values() if x.level_id == self.active_level_id), None)
        if level is None:
            return
        rows = [(room.room_id, f"{room.room_id} · {room.name}") for room in level.rooms.values()]
        ids = [r[0] for r in rows]
        displays = [r[1] for r in rows]
        combo = _heating_room_combo(self)
        if combo is None:
            return
        combo["values"] = tuple(displays)
        room_id = self.selected_room_id if self.selected_room_id in ids else (ids[0] if ids else None)
        if room_id:
            idx = ids.index(room_id)
            combo.current(idx)
            self.heating_room_var.set(room_id)

    def _refresh_context(self):
        original_refresh_context(self)
        self._sync_room_controls()
        if self.selected_room_id:
            self.heating_room_var.set(self.selected_room_id)

    def _room_changed(self):
        original_room_changed(self)
        if self.selected_room_id:
            self.heating_room_var.set(self.selected_room_id)
        self._draw_context()

    def _level_changed(self):
        original_level_changed(self)
        self._sync_room_controls()

    def _combo_selected(self, combo, labels):
        original_combo_selected(self, combo, labels)
        if getattr(self, "heating_room_var", None) is not None and combo.cget("textvariable") == str(self.heating_room_var):
            self.selected_room_id = self.heating_room_var.get()
            self.room_var.set(self.heating_room_var.get())
            self._refresh_context()
            self._draw_context()

    def _save_underfloor(self):
        original_save_underfloor(self)
        if self.workflow is None or not self.selected_room_id:
            return
        registry = ensure_mep_registry(self.workflow.model)
        systems = [s for s in registry.all_underfloor_systems if s.room_id == self.selected_room_id]
        if not systems:
            return
        system = systems[-1]
        mode = next((key for key, label in _ZONE_LABELS.items() if label == self.zone_mode_var.get()), "full")
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
        original_systems = None
        if registry is not None:
            original_systems = registry.underfloor_systems
            registry.underfloor_systems = {}
        try:
            original_draw_context(self)
        finally:
            if registry is not None and original_systems is not None:
                registry.underfloor_systems = original_systems
        if self.workflow is None or registry is None:
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
        zones = getattr(registry, "underfloor_zones", {})
        for system in registry.all_underfloor_systems:
            if system.level_id != active.level_id:
                continue
            room = active.rooms.get(system.room_id)
            if room is None:
                continue
            p, q = room.footprint.origin, room.footprint.max_point
            room_zones = [z for z in zones.values() if z.system_id == system.id]
            if not room_zones:
                room_zones = [UnderfloorZone(id="TEMP", system_id=system.id, room_id=system.room_id, level_id=system.level_id)]
            for zone in room_zones:
                zx1, zx2 = p.x, q.x
                if zone.mode == "half_a":
                    zx2 = p.x + (q.x - p.x) / 2.0
                elif zone.mode == "half_b":
                    zx1 = p.x + (q.x - p.x) / 2.0
                x1, y1 = xy(zx1, p.y)
                x2, y2 = xy(zx2, q.y)
                self.canvas.create_rectangle(x1 + 4, y2 + 4, x2 - 4, y1 - 4, outline="#1d4ed8", width=2, dash=(5, 3))
                spacing_px = max(6.0, system.pipe_spacing_m * scale)
                y = y2 + 8
                while y < y1 - 8:
                    self.canvas.create_line(x1 + 8, y, x2 - 8, y, fill="#2563eb", width=1)
                    y += spacing_px
                self.canvas.create_text((x1 + x2) / 2, y2 + 12, text=f"Podno · {zone.label}", fill="#1d4ed8", font=("Segoe UI", 9, "bold"))

    cls.__init__ = _init
    cls._refresh_context = _refresh_context
    cls._room_changed = _room_changed
    cls._level_changed = _level_changed
    cls._combo_selected = _combo_selected
    cls._save_underfloor = _save_underfloor
    cls._draw_context = _draw_context
    return cls
