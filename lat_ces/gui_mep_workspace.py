"""Unified MEP workspace over the verified ventilation, water and heating editors.

The workspace does not duplicate domain logic. It provides one selector/list over
BuildingModel.mep objects and delegates type-specific editing to the existing
VentilationOpening, WaterBranch and HeatingZone editors.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.gui_heating import HeatingMEPDraftingApp


class UnifiedMEPWorkspaceApp(HeatingMEPDraftingApp):
    """Single-window MEP selector with shared object navigation and deletion."""

    _TYPE_LABELS = {
        "all": "Svi MEP objekti",
        "ventilation": "Ventilacija",
        "water": "Voda",
        "heating": "Grijanje",
    }

    def __init__(self) -> None:
        self.mep_filter_var: tk.StringVar | None = None
        self.mep_selected_ref: tuple[str, str] | None = None
        super().__init__()
        self.canvas.bind("<Double-Button-1>", self._select_mep_from_canvas)

    def _build_side_panel(self, side: ttk.Frame) -> None:
        super()._build_side_panel(side)

        box = ttk.LabelFrame(side, text="MEP — zajednički selektor", padding=8)
        box.pack(fill="x", pady=(10, 0), before=self.heating_list.master)

        self.mep_filter_var = tk.StringVar(master=self, value="all")
        ttk.Label(box, text="Tip objekta").grid(row=0, column=0, sticky="w", pady=2)
        filter_combo = ttk.Combobox(
            box,
            textvariable=self.mep_filter_var,
            values=tuple(self._TYPE_LABELS),
            state="readonly",
            width=18,
        )
        filter_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)
        filter_combo.bind("<<ComboboxSelected>>", lambda _event: self._refresh_unified_mep())

        self.mep_list = tk.Listbox(box, height=8, exportselection=False)
        self.mep_list.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.mep_list.bind("<<ListboxSelect>>", self._select_unified_mep)
        self.mep_list.bind("<Double-Button-1>", self._select_unified_mep)

        buttons = ttk.Frame(box)
        buttons.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(buttons, text="Osvježi", command=self._refresh_unified_mep).pack(side="left", fill="x", expand=True)
        ttk.Button(buttons, text="Obriši odabrani", command=self._delete_unified_mep).pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.mep_status_var = tk.StringVar(master=self, value="Nije odabran MEP objekat")
        ttk.Label(box, textvariable=self.mep_status_var, wraplength=320).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(6, 0)
        )
        box.columnconfigure(1, weight=1)
        self._refresh_unified_mep()

    def _mep_registry(self):
        return ensure_mep_registry(self.workflow.model)

    def _all_unified_items(self) -> list[tuple[str, str, str, str]]:
        registry = self._mep_registry()
        items: list[tuple[str, str, str, str]] = []
        for opening in registry.all_ventilation_openings:
            items.append(("ventilation", opening.id, opening.room_id, f"ventilacija · {opening.kind} · Ø{opening.diameter_m:.3f} m"))
        for branch in registry.all_water_branches:
            items.append(("water", branch.id, branch.room_id, f"voda · {branch.service} · Ø{branch.diameter_m:.3f} m"))
        for zone in registry.all_heating_zones:
            items.append(("heating", zone.id, zone.room_id, f"grijanje · {zone.emitter_type} · {zone.design_supply_temp_c:.0f}/{zone.design_return_temp_c:.0f} °C"))
        return items

    def _filtered_unified_items(self) -> list[tuple[str, str, str, str]]:
        current = self.mep_filter_var.get() if self.mep_filter_var is not None else "all"
        items = self._all_unified_items()
        return items if current == "all" else [item for item in items if item[0] == current]

    def _refresh_unified_mep(self) -> None:
        if not hasattr(self, "mep_list"):
            return
        self.mep_list.delete(0, tk.END)
        for item_type, object_id, room_id, description in self._filtered_unified_items():
            label = self._TYPE_LABELS[item_type]
            self.mep_list.insert(tk.END, f"{label} · {object_id} · {room_id} · {description}")
        self._draw_unified_selection_marker()

    def _select_unified_mep(self, _event: tk.Event | None = None) -> None:
        selection = self.mep_list.curselection()
        if not selection:
            return
        item = self._filtered_unified_items()[selection[0]]
        item_type, object_id, room_id, description = item
        self.mep_selected_ref = (item_type, object_id)
        self.mep_status_var.set(f"Odabrano: {self._TYPE_LABELS[item_type]} · {object_id} · prostorija {room_id}\n{description}")

        if item_type == "ventilation":
            self.ventilation_selected_id = object_id
            opening_index = next(i for i, opening in enumerate(self._mep_registry().all_ventilation_openings) if opening.id == object_id)
            self.vent_list.selection_clear(0, tk.END)
            self.vent_list.selection_set(opening_index)
            self._select_ventilation(None)
        elif item_type == "water":
            self.water_selected_id = object_id
            branch_index = next(i for i, branch in enumerate(self._mep_registry().all_water_branches) if branch.id == object_id)
            self.water_list.selection_clear(0, tk.END)
            self.water_list.selection_set(branch_index)
            self._select_water(None)
        else:
            self.heating_selected_id = object_id
            zone_index = next(i for i, zone in enumerate(self._mep_registry().all_heating_zones) if zone.id == object_id)
            self.heating_list.selection_clear(0, tk.END)
            self.heating_list.selection_set(zone_index)
            self._select_heating_zone(None)
        self._draw_unified_selection_marker()

    def _delete_unified_mep(self) -> None:
        if self.mep_selected_ref is None:
            return
        item_type, object_id = self.mep_selected_ref
        registry = self._mep_registry()
        if item_type == "ventilation":
            registry.remove_ventilation_opening(object_id)
            self.ventilation_selected_id = None
        elif item_type == "water":
            registry.remove_water_branch(object_id)
            self.water_selected_id = None
        else:
            registry.remove_heating_zone(object_id)
            self.heating_selected_id = None
        self.mep_selected_ref = None
        self.mep_status_var.set("Nije odabran MEP objekat")
        self._refresh_mep_editor()
        self._refresh_water_editor()
        self._refresh_heating_editor()
        self._refresh_unified_mep()
        self.status_var.set(f"MEP objekat obrisan: {object_id}")
        self.refresh_view()

    def _refresh_mep_editor(self) -> None:
        super()._refresh_mep_editor()
        if hasattr(self, "mep_list"):
            self._refresh_unified_mep()

    def _refresh_water_editor(self) -> None:
        super()._refresh_water_editor()
        if hasattr(self, "mep_list"):
            self._refresh_unified_mep()

    def _refresh_heating_editor(self) -> None:
        super()._refresh_heating_editor()
        if hasattr(self, "mep_list"):
            self._refresh_unified_mep()

    def _draw_unified_selection_marker(self) -> None:
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("unified-mep-selection")
        if self.mep_selected_ref is None:
            return
        item_type, object_id = self.mep_selected_ref
        registry = self._mep_registry()
        if item_type == "ventilation":
            opening = registry.ventilation_openings.get(object_id)
            if opening is None:
                return
            from lat_ces.building.floor_plan import Point2D
            x, y = self.model_to_canvas(Point2D(opening.x_m, opening.y_m))
            self.canvas.create_oval(x - 12, y - 12, x + 12, y + 12, outline="#111827", width=3, tags="unified-mep-selection")
        elif item_type == "water":
            branch = registry.water_branches.get(object_id)
            if branch is None:
                return
            from lat_ces.building.floor_plan import Point2D
            x1, y1 = self.model_to_canvas(Point2D(branch.x1_m, branch.y1_m))
            x2, y2 = self.model_to_canvas(Point2D(branch.x2_m, branch.y2_m))
            self.canvas.create_line(x1, y1, x2, y2, fill="#111827", width=4, dash=(6, 3), tags="unified-mep-selection")
        else:
            zone = registry.heating_zones.get(object_id)
            if zone is None:
                return
            room = next((r for r in self.active_level.rooms.values() if r.room_id == zone.room_id), None)
            if room is None:
                return
            from lat_ces.building.floor_plan import Point2D
            p, q = room.footprint.origin, room.footprint.max_point
            x1, y1 = self.model_to_canvas(Point2D(p.x, p.y))
            x2, y2 = self.model_to_canvas(Point2D(q.x, q.y))
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#111827", width=4, dash=(6, 3), tags="unified-mep-selection")

    def _select_mep_from_canvas(self, event: tk.Event) -> None:
        point = self.canvas_to_model(event.x, event.y)
        registry = self._mep_registry()
        candidates: list[tuple[float, str, str]] = []
        for opening in registry.all_ventilation_openings:
            distance = ((opening.x_m - point.x) ** 2 + (opening.y_m - point.y) ** 2) ** 0.5
            if distance <= 0.35:
                candidates.append((distance, "ventilation", opening.id))
        for branch in registry.all_water_branches:
            distance = self._point_to_segment_distance(point.x, point.y, branch.x1_m, branch.y1_m, branch.x2_m, branch.y2_m)
            if distance <= 0.20:
                candidates.append((distance, "water", branch.id))
        for zone in registry.all_heating_zones:
            room = next((r for r in self.active_level.rooms.values() if r.room_id == zone.room_id), None)
            if room is None:
                continue
            p, q = room.footprint.origin, room.footprint.max_point
            if p.x <= point.x <= q.x and p.y <= point.y <= q.y:
                candidates.append((0.0, "heating", zone.id))
        if not candidates:
            return
        _, item_type, object_id = min(candidates, key=lambda item: item[0])
        current = self.mep_filter_var.get() if self.mep_filter_var is not None else "all"
        if current != "all" and current != item_type:
            self.mep_filter_var.set(item_type)
            self._refresh_unified_mep()
        target = (item_type, object_id)
        items = self._filtered_unified_items()
        for index, item in enumerate(items):
            if item[:2] == target:
                self.mep_list.selection_clear(0, tk.END)
                self.mep_list.selection_set(index)
                self.mep_list.see(index)
                self._select_unified_mep()
                return

    @staticmethod
    def _point_to_segment_distance(px: float, py: float, x1: float, y1: float, x2: float, y2: float) -> float:
        dx, dy = x2 - x1, y2 - y1
        length_sq = dx * dx + dy * dy
        if length_sq <= 1e-12:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / length_sq))
        cx, cy = x1 + t * dx, y1 + t * dy
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        self._draw_unified_selection_marker()


def main() -> None:
    UnifiedMEPWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
