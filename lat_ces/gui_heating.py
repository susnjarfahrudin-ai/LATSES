"""HeatingZone-enabled drafting GUI for the interactive MEP layer.

HeatingZone is a room-level object. The GUI captures emitter intent, design
temperatures, and real design heat-load/mass-flow inputs; heat calculations
remain in the engineering service.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from uuid import uuid4

from lat_ces.building.floor_plan import Point2D
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building_model.systems import HeatingZone
from lat_ces.gui_water import WaterMEPDraftingApp


class HeatingMEPDraftingApp(WaterMEPDraftingApp):
    """MEP drafting GUI with interactive HeatingZone creation/editing."""

    def __init__(self) -> None:
        self.heating_selected_id: str | None = None
        super().__init__()

    def _build_side_panel(self, side: ttk.Frame) -> None:
        super()._build_side_panel(side)

        self.heating_room_var = tk.StringVar(master=self, value="")
        self.heating_emitter_var = tk.StringVar(master=self, value="underfloor")
        self.heating_supply_var = tk.StringVar(master=self, value="35.0")
        self.heating_return_var = tk.StringVar(master=self, value="28.0")
        self.heating_target_var = tk.StringVar(master=self, value="20.0")
        self.heating_load_var = tk.StringVar(master=self, value="")
        self.heating_flow_var = tk.StringVar(master=self, value="")

        box = ttk.LabelFrame(side, text="MEP — zona grijanja", padding=8)
        box.pack(fill="x", pady=(10, 0))

        ttk.Label(box, text="Prostorija").grid(row=0, column=0, sticky="w", pady=2)
        self.heating_room_combo = ttk.Combobox(box, textvariable=self.heating_room_var, state="readonly", width=22)
        self.heating_room_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)

        ttk.Label(box, text="Emiter").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(
            box,
            textvariable=self.heating_emitter_var,
            values=("underfloor", "radiator", "wall", "ceiling", "convector", "air", "combined"),
            state="readonly",
            width=16,
        ).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)
        self._field(box, "Polaz (°C)", self.heating_supply_var, 2)
        self._field(box, "Povrat (°C)", self.heating_return_var, 3)
        self._field(box, "Cilj prostorije (°C)", self.heating_target_var, 4)
        self._field(box, "Projektno opterećenje (W)", self.heating_load_var, 5)
        self._field(box, "Maseni protok (kg/s)", self.heating_flow_var, 6)

        add_row = ttk.Frame(box)
        add_row.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(add_row, text="＋ Dodaj zonu", command=self._add_heating_zone).pack(side="left", fill="x", expand=True)
        ttk.Button(add_row, text="Sačuvaj izmjenu", command=self._update_heating_zone).pack(side="left", fill="x", expand=True, padx=(6, 0))
        ttk.Button(add_row, text="Obriši", command=self._delete_heating_zone).pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.heating_list = tk.Listbox(box, height=5, exportselection=False)
        self.heating_list.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.heating_list.bind("<<ListboxSelect>>", self._select_heating_zone)
        ttk.Label(
            box,
            text="Unesi projektno opterećenje ili maseni protok. Ako oba postoje, servis provjerava njihovu međusobnu konzistentnost.",
            wraplength=320,
        ).grid(row=9, column=0, columnspan=2, sticky="w", pady=(6, 0))
        box.columnconfigure(1, weight=1)
        self._refresh_heating_editor()

    def _heating_registry(self):
        return ensure_mep_registry(self.workflow.model)

    def _room_map_for_heating(self) -> dict[str, object]:
        return {room.room_id: room for room in self.active_level.rooms.values()}

    def _refresh_heating_editor(self) -> None:
        if not hasattr(self, "heating_room_combo"):
            return
        room_map = self._room_map_for_heating()
        values = [f"{room.name} [{room.room_id}]" for room in room_map.values()]
        self._heating_display_to_id = {f"{room.name} [{room.room_id}]": room.room_id for room in room_map.values()}
        self.heating_room_combo["values"] = values
        if values and self.heating_room_var.get() not in values:
            self.heating_room_var.set(values[0])
        self.heating_list.delete(0, tk.END)
        for zone in self._heating_registry().all_heating_zones:
            load = f" · {zone.room_heat_load_w:.0f} W" if zone.room_heat_load_w is not None else ""
            flow = f" · {zone.mass_flow_kg_s:.4f} kg/s" if zone.mass_flow_kg_s is not None else ""
            self.heating_list.insert(
                tk.END,
                f"{zone.id} · {zone.emitter_type} · {zone.design_supply_temp_c:.1f}/{zone.design_return_temp_c:.1f} °C{load}{flow} · {zone.room_id}",
            )

    def _heating_room_id(self) -> str:
        room_id = self._heating_display_to_id.get(self.heating_room_var.get().strip())
        if not room_id:
            raise ValueError("Izaberi prostoriju za zonu grijanja")
        return room_id

    @staticmethod
    def _temperature(value: str, label: str) -> float:
        try:
            return float(value)
        except ValueError as exc:
            raise ValueError(f"{label} mora biti broj") from exc

    @staticmethod
    def _optional_positive(value: str, label: str) -> float | None:
        text = value.strip()
        if not text:
            return None
        try:
            number = float(text)
        except ValueError as exc:
            raise ValueError(f"{label} mora biti broj") from exc
        if number <= 0:
            raise ValueError(f"{label} mora biti > 0")
        return number

    def _zone_from_form(self, zone_id: str) -> HeatingZone:
        supply = self._temperature(self.heating_supply_var.get(), "Polazna temperatura")
        return_temp = self._temperature(self.heating_return_var.get(), "Povratna temperatura")
        target = self._temperature(self.heating_target_var.get(), "Ciljna temperatura")
        if supply <= return_temp:
            raise ValueError("Polazna temperatura mora biti viša od povratne")
        if target < -50 or target > 50:
            raise ValueError("Ciljna temperatura mora biti u rasponu -50 do 50 °C")
        return HeatingZone(
            id=zone_id,
            room_id=self._heating_room_id(),
            emitter_type=self.heating_emitter_var.get(),
            design_supply_temp_c=supply,
            design_return_temp_c=return_temp,
            target_indoor_temp_c=target,
            room_heat_load_w=self._optional_positive(self.heating_load_var.get(), "Projektno opterećenje"),
            mass_flow_kg_s=self._optional_positive(self.heating_flow_var.get(), "Maseni protok"),
        )

    def _add_heating_zone(self) -> None:
        try:
            zone = self._zone_from_form(f"HZ-{uuid4().hex[:8].upper()}")
            if zone.room_id not in self._room_map_for_heating():
                raise ValueError("Izabrana prostorija više ne postoji")
            self._heating_registry().add_heating_zone(zone)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Grijanje", str(exc), parent=self)
            return
        self.heating_selected_id = zone.id
        self._refresh_heating_editor()
        self.status_var.set(f"Zona grijanja dodata: {zone.id} · {zone.emitter_type}")
        self.refresh_view()

    def _select_heating_zone(self, _event: tk.Event) -> None:
        selection = self.heating_list.curselection()
        if not selection:
            return
        zone = self._heating_registry().all_heating_zones[selection[0]]
        self.heating_selected_id = zone.id
        room = self._room_map_for_heating().get(zone.room_id)
        if room:
            self.heating_room_var.set(f"{room.name} [{room.room_id}]")
        self.heating_emitter_var.set(zone.emitter_type)
        self.heating_supply_var.set(f"{zone.design_supply_temp_c:.1f}")
        self.heating_return_var.set(f"{zone.design_return_temp_c:.1f}")
        self.heating_target_var.set(f"{zone.target_indoor_temp_c:.1f}")
        self.heating_load_var.set("" if zone.room_heat_load_w is None else f"{zone.room_heat_load_w:.1f}")
        self.heating_flow_var.set("" if zone.mass_flow_kg_s is None else f"{zone.mass_flow_kg_s:.6f}")

    def _update_heating_zone(self) -> None:
        if not self.heating_selected_id:
            messagebox.showwarning("LAT-CES — Grijanje", "Prvo izaberi zonu iz liste.", parent=self)
            return
        try:
            zone = self._zone_from_form(self.heating_selected_id)
            if zone.room_id not in self._room_map_for_heating():
                raise ValueError("Izabrana prostorija više ne postoji")
            self._heating_registry().update_heating_zone(zone.id, **zone.__dict__)
        except (KeyError, ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Grijanje", str(exc), parent=self)
            return
        self._refresh_heating_editor()
        self.status_var.set(f"Zona grijanja izmijenjena: {zone.id}")
        self.refresh_view()

    def _delete_heating_zone(self) -> None:
        if not self.heating_selected_id:
            return
        deleted = self._heating_registry().remove_heating_zone(self.heating_selected_id)
        self.heating_selected_id = None
        self._refresh_heating_editor()
        self.status_var.set(f"Zona grijanja obrisana: {deleted.id}")
        self.refresh_view()

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        if not hasattr(self, "heating_list"):
            return
        room_map = self._room_map_for_heating()
        for zone in self._heating_registry().all_heating_zones:
            room = room_map.get(zone.room_id)
            if room is None:
                continue
            p = room.footprint.origin
            q = room.footprint.max_point
            x1, y1 = self.model_to_canvas(Point2D(p.x, p.y))
            x2, y2 = self.model_to_canvas(Point2D(q.x, q.y))
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#dc2626", dash=(4, 3), width=2)
            load_label = "" if zone.room_heat_load_w is None else f" · {zone.room_heat_load_w:.0f} W"
            self.canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                text=f"GRIJANJE · {zone.emitter_type}\n{zone.design_supply_temp_c:.0f}/{zone.design_return_temp_c:.0f} °C{load_label}",
                fill="#b91c1c",
                font=("Segoe UI", 8, "bold"),
            )


def main() -> None:
    HeatingMEPDraftingApp().mainloop()


if __name__ == "__main__":
    main()
