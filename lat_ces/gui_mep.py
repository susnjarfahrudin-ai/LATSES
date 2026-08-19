"""MEP-enabled drafting GUI for the first interactive ventilation slice.

The GUI creates and edits real VentilationOpening objects owned by the current
BuildingModel's MEP registry. Placement is performed by clicking inside a room;
widgets only collect design intent and never hardcode engineering results.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from uuid import uuid4

from lat_ces.building.floor_plan import Point2D
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building_model.systems import VentilationOpening
from lat_ces.gui_drafting import DraftingLATCESApp


class MEPEnabledDraftingApp(DraftingLATCESApp):
    """Drafting GUI with interactive VentilationOpening creation/editing."""

    def __init__(self) -> None:
        self.ventilation_placing = False
        self.ventilation_selected_id: str | None = None
        super().__init__()
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self._mep_click)

    def _build_side_panel(self, side: ttk.Frame) -> None:
        super()._build_side_panel(side)

        self.vent_room_var = tk.StringVar(master=self, value="")
        self.vent_kind_var = tk.StringVar(master=self, value="supply")
        self.vent_diameter_var = tk.StringVar(master=self, value="0.10")
        self.vent_velocity_var = tk.StringVar(master=self, value="0.05")
        self.vent_elevation_var = tk.StringVar(master=self, value="0.70")
        self.vent_x_var = tk.StringVar(master=self, value="0.00")
        self.vent_y_var = tk.StringVar(master=self, value="0.00")

        box = ttk.LabelFrame(side, text="MEP — ventilacijski otvor", padding=8)
        box.pack(fill="x", pady=(10, 0))

        ttk.Label(box, text="Prostorija").grid(row=0, column=0, sticky="w", pady=2)
        self.vent_room_combo = ttk.Combobox(box, textvariable=self.vent_room_var, state="readonly", width=22)
        self.vent_room_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)
        self.vent_room_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_room_coordinates())

        ttk.Label(box, text="Tip").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(box, textvariable=self.vent_kind_var, values=("supply", "extract"), state="readonly", width=12).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)
        self._field(box, "Prečnik (m)", self.vent_diameter_var, 2)
        self._field(box, "Brzina (m/s)", self.vent_velocity_var, 3)
        self._field(box, "Visina (m)", self.vent_elevation_var, 4)
        self._field(box, "X (m)", self.vent_x_var, 5)
        self._field(box, "Y (m)", self.vent_y_var, 6)

        place_row = ttk.Frame(box)
        place_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(place_row, text="＋ Postavi na tlocrt", command=self._start_ventilation_placement).pack(side="left", fill="x", expand=True)
        ttk.Button(place_row, text="Dodaj", command=self._add_ventilation).pack(side="left", fill="x", expand=True, padx=(6, 0))

        edit_row = ttk.Frame(box)
        edit_row.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(edit_row, text="Sačuvaj izmjenu", command=self._update_ventilation).pack(side="left", fill="x", expand=True)
        ttk.Button(edit_row, text="Obriši", command=self._delete_ventilation).pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.vent_list = tk.Listbox(box, height=5, exportselection=False)
        self.vent_list.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.vent_list.bind("<<ListboxSelect>>", self._select_ventilation)
        ttk.Label(
            box,
            text="Klik 'Postavi na tlocrt', zatim klikni unutar prostorije. Objekat ulazi direktno u BuildingModel.mep.",
            wraplength=320,
        ).grid(row=10, column=0, columnspan=2, sticky="w", pady=(6, 0))
        box.columnconfigure(1, weight=1)
        self._refresh_mep_editor()

    def _mep_registry(self):
        return ensure_mep_registry(self.workflow.model)

    def _room_map(self) -> dict[str, object]:
        return {room.room_id: room for room in self.active_level.rooms.values()}

    def _refresh_mep_editor(self) -> None:
        if not hasattr(self, "vent_room_combo"):
            return
        room_map = self._room_map()
        values = [f"{room.name} [{room.room_id}]" for room in room_map.values()]
        self._room_display_to_id = {f"{room.name} [{room.room_id}]": room.room_id for room in room_map.values()}
        self.vent_room_combo["values"] = values
        if values and self.vent_room_var.get() not in values:
            self.vent_room_var.set(values[0])
        self.vent_list.delete(0, tk.END)
        for opening in self._mep_registry().all_ventilation_openings:
            self.vent_list.insert(
                tk.END,
                f"{opening.id} · {opening.kind} · {opening.diameter_m:.2f} m · {opening.room_id} · ({opening.x_m:.2f}, {opening.y_m:.2f})",
            )

    def _start_ventilation_placement(self) -> None:
        self._refresh_mep_editor()
        if not self._room_map():
            messagebox.showwarning("LAT-CES — Ventilacija", "Prvo dodaj barem jednu prostoriju.", parent=self)
            return
        self.ventilation_placing = True
        self.view_step.set(3)
        self.goto_step()
        self.status_var.set("VENTILACIJA: klikni unutar prostorije na mjestu otvora.")

    def _mep_click(self, event: tk.Event) -> None:
        if self.ventilation_placing:
            point = self.snap_point(self.canvas_to_model(event.x, event.y))
            room = self._room_at_point(point)
            if room is None:
                messagebox.showwarning("LAT-CES — Ventilacija", "Otvor mora biti postavljen unutar prostorije.", parent=self)
                return
            self.ventilation_placing = False
            self.vent_room_var.set(f"{room.name} [{room.room_id}]")
            self.vent_x_var.set(f"{point.x:.2f}")
            self.vent_y_var.set(f"{point.y:.2f}")
            self._add_ventilation()
            return
        self._draft_click(event)

    def _room_at_point(self, point: Point2D):
        for room in self.active_level.rooms.values():
            origin = room.footprint.origin
            maximum = room.footprint.max_point
            if origin.x <= point.x <= maximum.x and origin.y <= point.y <= maximum.y:
                return room
        return None

    def _room_id_from_display(self) -> str:
        display = self.vent_room_var.get().strip()
        room_id = self._room_display_to_id.get(display)
        if not room_id:
            raise ValueError("Izaberi prostoriju za ventilacijski otvor")
        return room_id

    @staticmethod
    def _positive_number(value: str, label: str, minimum: float = 0.0) -> float:
        try:
            number = float(value)
        except ValueError as exc:
            raise ValueError(f"{label} mora biti broj") from exc
        if number <= minimum:
            raise ValueError(f"{label} mora biti > {minimum}")
        return number

    def _opening_from_form(self, opening_id: str) -> VentilationOpening:
        return VentilationOpening(
            id=opening_id,
            room_id=self._room_id_from_display(),
            kind=self.vent_kind_var.get(),
            diameter_m=self._positive_number(self.vent_diameter_var.get(), "Prečnik"),
            design_velocity_m_s=self._positive_number(self.vent_velocity_var.get(), "Brzina"),
            elevation_m=float(self.vent_elevation_var.get()),
            x_m=float(self.vent_x_var.get()),
            y_m=float(self.vent_y_var.get()),
        )

    def _add_ventilation(self) -> None:
        try:
            opening = self._opening_from_form(f"VO-{uuid4().hex[:8].upper()}")
            room = self._room_map().get(opening.room_id)
            if room is None:
                raise ValueError("Izabrana prostorija više ne postoji")
            origin, maximum = room.footprint.origin, room.footprint.max_point
            if not (origin.x <= opening.x_m <= maximum.x and origin.y <= opening.y_m <= maximum.y):
                raise ValueError("Koordinate otvora moraju biti unutar izabrane prostorije")
            self._mep_registry().add_ventilation_opening(opening)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Ventilacija", str(exc), parent=self)
            return
        self.ventilation_selected_id = opening.id
        self._refresh_mep_editor()
        self.status_var.set(f"Ventilacijski otvor dodat: {opening.id} · {opening.design_flow_m3_h:.2f} m³/h")
        self.refresh_view()

    def _select_ventilation(self, _event: tk.Event) -> None:
        selection = self.vent_list.curselection()
        if not selection:
            return
        opening = self._mep_registry().all_ventilation_openings[selection[0]]
        self.ventilation_selected_id = opening.id
        room = self._room_map().get(opening.room_id)
        if room:
            self.vent_room_var.set(f"{room.name} [{room.room_id}]")
        self.vent_kind_var.set(opening.kind)
        self.vent_diameter_var.set(f"{opening.diameter_m:.3f}")
        self.vent_velocity_var.set(f"{opening.design_velocity_m_s:.3f}")
        self.vent_elevation_var.set(f"{opening.elevation_m:.3f}")
        self.vent_x_var.set(f"{opening.x_m:.3f}")
        self.vent_y_var.set(f"{opening.y_m:.3f}")

    def _update_ventilation(self) -> None:
        if not self.ventilation_selected_id:
            messagebox.showwarning("LAT-CES — Ventilacija", "Prvo izaberi otvor iz liste.", parent=self)
            return
        try:
            current = self._mep_registry().ventilation_openings[self.ventilation_selected_id]
            updated = self._opening_from_form(current.id)
            self._mep_registry().ventilation_openings[current.id] = updated
        except (KeyError, ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Ventilacija", str(exc), parent=self)
            return
        self._refresh_mep_editor()
        self.status_var.set(f"Ventilacijski otvor izmijenjen: {updated.id}")
        self.refresh_view()

    def _delete_ventilation(self) -> None:
        if not self.ventilation_selected_id:
            return
        deleted = self._mep_registry().remove_ventilation_opening(self.ventilation_selected_id)
        self.ventilation_selected_id = None
        self._refresh_mep_editor()
        self.status_var.set(f"Ventilacijski otvor obrisan: {deleted.id}")
        self.refresh_view()

    def _sync_room_coordinates(self) -> None:
        room_id = self._room_id_from_display()
        room = self._room_map()[room_id]
        origin = room.footprint.origin
        maximum = room.footprint.max_point
        self.vent_x_var.set(f"{(origin.x + maximum.x) / 2.0:.2f}")
        self.vent_y_var.set(f"{(origin.y + maximum.y) / 2.0:.2f}")

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        if not hasattr(self, "vent_list"):
            return
        room_ids = {room.room_id for room in self.active_level.rooms.values()}
        for opening in self._mep_registry().all_ventilation_openings:
            if opening.room_id not in room_ids:
                continue
            x, y = self.model_to_canvas(Point2D(opening.x_m, opening.y_m))
            radius = max(5.0, min(12.0, opening.diameter_m * 40.0))
            outline = "#2563eb" if opening.kind == "supply" else "#dc2626"
            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=outline, width=3)
            self.canvas.create_text(x + radius + 4, y, text=f"{opening.kind} · Ø{opening.diameter_m:.2f}", anchor="w", fill=outline, font=("Segoe UI", 8, "bold"))
        if self.ventilation_placing:
            self.canvas.create_text(20, 66, text="VENTILACIJA — klik unutar prostorije za novi otvor", anchor="nw", fill="#2563eb", font=("Segoe UI", 10, "bold"))


def main() -> None:
    MEPEnabledDraftingApp().mainloop()


if __name__ == "__main__":
    main()
