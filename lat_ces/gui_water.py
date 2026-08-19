"""WaterBranch-enabled drafting GUI for the interactive MEP layer.

The editor creates and edits real WaterBranch objects owned by BuildingModel.mep.
Placement is graphical: the user clicks a start point and an end point inside one
room. Hydraulic calculations remain in the water engine, not in the GUI.
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk
from uuid import uuid4

from lat_ces.building.floor_plan import Point2D
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building_model.systems import WaterBranch
from lat_ces.gui_mep import MEPEnabledDraftingApp


class WaterMEPDraftingApp(MEPEnabledDraftingApp):
    """MEP drafting GUI with interactive WaterBranch creation/editing."""

    def __init__(self) -> None:
        self.water_placing = False
        self.water_start: Point2D | None = None
        self.water_selected_id: str | None = None
        super().__init__()
        self.canvas.bind("<Button-1>", self._water_click, add="+")

    def _build_side_panel(self, side: ttk.Frame) -> None:
        super()._build_side_panel(side)

        self.water_room_var = tk.StringVar(master=self, value="")
        self.water_service_var = tk.StringVar(master=self, value="cold_water")
        self.water_diameter_var = tk.StringVar(master=self, value="0.020")
        self.water_flow_var = tk.StringVar(master=self, value="0.00020")
        self.water_length_var = tk.StringVar(master=self, value="0.00")
        self.water_x1_var = tk.StringVar(master=self, value="0.00")
        self.water_y1_var = tk.StringVar(master=self, value="0.00")
        self.water_x2_var = tk.StringVar(master=self, value="0.00")
        self.water_y2_var = tk.StringVar(master=self, value="0.00")

        box = ttk.LabelFrame(side, text="MEP — vodna grana", padding=8)
        box.pack(fill="x", pady=(10, 0))

        ttk.Label(box, text="Prostorija").grid(row=0, column=0, sticky="w", pady=2)
        self.water_room_combo = ttk.Combobox(box, textvariable=self.water_room_var, state="readonly", width=22)
        self.water_room_combo.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=2)
        self.water_room_combo.bind("<<ComboboxSelected>>", lambda _event: self._sync_water_coordinates())

        ttk.Label(box, text="Servis").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Combobox(
            box,
            textvariable=self.water_service_var,
            values=("cold_water", "dhw", "return", "drain"),
            state="readonly",
            width=16,
        ).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=2)
        self._field(box, "Prečnik (m)", self.water_diameter_var, 2)
        self._field(box, "Protok (m³/s)", self.water_flow_var, 3)
        self._field(box, "Dužina (m)", self.water_length_var, 4)
        self._field(box, "X1 (m)", self.water_x1_var, 5)
        self._field(box, "Y1 (m)", self.water_y1_var, 6)
        self._field(box, "X2 (m)", self.water_x2_var, 7)
        self._field(box, "Y2 (m)", self.water_y2_var, 8)

        place_row = ttk.Frame(box)
        place_row.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(place_row, text="＋ Nacrtaj granu", command=self._start_water_placement).pack(side="left", fill="x", expand=True)
        ttk.Button(place_row, text="Dodaj", command=self._add_water).pack(side="left", fill="x", expand=True, padx=(6, 0))

        edit_row = ttk.Frame(box)
        edit_row.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Button(edit_row, text="Sačuvaj izmjenu", command=self._update_water).pack(side="left", fill="x", expand=True)
        ttk.Button(edit_row, text="Obriši", command=self._delete_water).pack(side="left", fill="x", expand=True, padx=(6, 0))

        self.water_list = tk.Listbox(box, height=5, exportselection=False)
        self.water_list.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        self.water_list.bind("<<ListboxSelect>>", self._select_water)
        ttk.Label(
            box,
            text="Nacrtaj granu klikom početne i završne tačke unutar iste prostorije. Proračun ostaje u water engine-u.",
            wraplength=320,
        ).grid(row=12, column=0, columnspan=2, sticky="w", pady=(6, 0))
        box.columnconfigure(1, weight=1)
        self._refresh_water_editor()

    def _water_registry(self):
        return ensure_mep_registry(self.workflow.model)

    def _refresh_water_editor(self) -> None:
        if not hasattr(self, "water_room_combo"):
            return
        room_map = {room.room_id: room for room in self.active_level.rooms.values()}
        values = [f"{room.name} [{room.room_id}]" for room in room_map.values()]
        self._water_display_to_id = {f"{room.name} [{room.room_id}]": room.room_id for room in room_map.values()}
        self.water_room_combo["values"] = values
        if values and self.water_room_var.get() not in values:
            self.water_room_var.set(values[0])
        self.water_list.delete(0, tk.END)
        for branch in self._water_registry().all_water_branches:
            self.water_list.insert(
                tk.END,
                f"{branch.id} · {branch.service} · Ø{branch.diameter_m:.3f} · {branch.design_flow_m3_s:.5f} m³/s · {branch.room_id}",
            )

    def _water_room_id(self) -> str:
        room_id = self._water_display_to_id.get(self.water_room_var.get().strip())
        if not room_id:
            raise ValueError("Izaberi prostoriju za vodnu granu")
        return room_id

    @staticmethod
    def _positive(value: str, label: str, *, allow_zero: bool = False) -> float:
        try:
            number = float(value)
        except ValueError as exc:
            raise ValueError(f"{label} mora biti broj") from exc
        if allow_zero and number >= 0:
            return number
        if number > 0:
            return number
        raise ValueError(f"{label} mora biti {'≥' if allow_zero else '>'} 0")

    def _sync_water_coordinates(self) -> None:
        room_id = self._water_room_id()
        room = next(room for room in self.active_level.rooms.values() if room.room_id == room_id)
        origin, maximum = room.footprint.origin, room.footprint.max_point
        cx, cy = (origin.x + maximum.x) / 2.0, (origin.y + maximum.y) / 2.0
        self.water_x1_var.set(f"{max(origin.x, cx - 1.0):.2f}")
        self.water_y1_var.set(f"{cy:.2f}")
        self.water_x2_var.set(f"{min(maximum.x, cx + 1.0):.2f}")
        self.water_y2_var.set(f"{cy:.2f}")
        self.water_length_var.set(f"{math.hypot(float(self.water_x2_var.get()) - float(self.water_x1_var.get()), float(self.water_y2_var.get()) - float(self.water_y1_var.get())):.2f}")

    def _start_water_placement(self) -> None:
        self._refresh_water_editor()
        if not any(self.active_level.rooms.values()):
            messagebox.showwarning("LAT-CES — Voda", "Prvo dodaj barem jednu prostoriju.", parent=self)
            return
        self.water_placing = True
        self.water_start = None
        self.view_step.set(3)
        self.goto_step()
        self.status_var.set("VODA: klikni početak grane, zatim završetak unutar iste prostorije.")

    def _room_at_point_for_water(self, point: Point2D):
        for room in self.active_level.rooms.values():
            origin = room.footprint.origin
            maximum = room.footprint.max_point
            if origin.x <= point.x <= maximum.x and origin.y <= point.y <= maximum.y:
                return room
        return None

    def _water_click(self, event: tk.Event) -> None:
        if not self.water_placing:
            return
        point = self.snap_point(self.canvas_to_model(event.x, event.y))
        room = self._room_at_point_for_water(point)
        if room is None:
            messagebox.showwarning("LAT-CES — Voda", "Vodna grana mora početi i završiti unutar prostorije.", parent=self)
            return
        if self.water_start is None:
            self.water_start = point
            self.water_room_var.set(f"{room.name} [{room.room_id}]")
            self.water_x1_var.set(f"{point.x:.2f}")
            self.water_y1_var.set(f"{point.y:.2f}")
            self.status_var.set("VODA: sada klikni završnu tačku grane.")
            return
        self.water_x2_var.set(f"{point.x:.2f}")
        self.water_y2_var.set(f"{point.y:.2f}")
        length = math.hypot(point.x - self.water_start.x, point.y - self.water_start.y)
        self.water_length_var.set(f"{length:.2f}")
        self.water_placing = False
        self._add_water()

    def _branch_from_form(self, branch_id: str) -> WaterBranch:
        return WaterBranch(
            id=branch_id,
            room_id=self._water_room_id(),
            service=self.water_service_var.get(),
            diameter_m=self._positive(self.water_diameter_var.get(), "Prečnik"),
            design_flow_m3_s=self._positive(self.water_flow_var.get(), "Protok", allow_zero=True),
            length_m=self._positive(self.water_length_var.get(), "Dužina"),
            x1_m=self._positive(self.water_x1_var.get(), "X1", allow_zero=True),
            y1_m=self._positive(self.water_y1_var.get(), "Y1", allow_zero=True),
            x2_m=self._positive(self.water_x2_var.get(), "X2", allow_zero=True),
            y2_m=self._positive(self.water_y2_var.get(), "Y2", allow_zero=True),
        )

    def _validate_branch_room(self, branch: WaterBranch) -> None:
        room = next((room for room in self.active_level.rooms.values() if room.room_id == branch.room_id), None)
        if room is None:
            raise ValueError("Izabrana prostorija više ne postoji")
        origin, maximum = room.footprint.origin, room.footprint.max_point
        for x, y, label in (
            (branch.x1_m, branch.y1_m, "Početna tačka"),
            (branch.x2_m, branch.y2_m, "Završna tačka"),
        ):
            if not (origin.x <= x <= maximum.x and origin.y <= y <= maximum.y):
                raise ValueError(f"{label} vodne grane mora biti unutar prostorije")

    def _add_water(self) -> None:
        try:
            branch = self._branch_from_form(f"WB-{uuid4().hex[:8].upper()}")
            self._validate_branch_room(branch)
            self._water_registry().add_water_branch(branch)
        except (ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Voda", str(exc), parent=self)
            return
        self.water_selected_id = branch.id
        self._refresh_water_editor()
        self.status_var.set(f"Vodna grana dodata: {branch.id} · {branch.length_m:.2f} m")
        self.refresh_view()

    def _select_water(self, _event: tk.Event) -> None:
        selection = self.water_list.curselection()
        if not selection:
            return
        branch = self._water_registry().all_water_branches[selection[0]]
        self.water_selected_id = branch.id
        room = next((room for room in self.active_level.rooms.values() if room.room_id == branch.room_id), None)
        if room:
            self.water_room_var.set(f"{room.name} [{room.room_id}]")
        self.water_service_var.set(branch.service)
        self.water_diameter_var.set(f"{branch.diameter_m:.4f}")
        self.water_flow_var.set(f"{branch.design_flow_m3_s:.6f}")
        self.water_length_var.set(f"{branch.length_m:.3f}")
        self.water_x1_var.set(f"{branch.x1_m:.3f}")
        self.water_y1_var.set(f"{branch.y1_m:.3f}")
        self.water_x2_var.set(f"{branch.x2_m:.3f}")
        self.water_y2_var.set(f"{branch.y2_m:.3f}")

    def _update_water(self) -> None:
        if not self.water_selected_id:
            messagebox.showwarning("LAT-CES — Voda", "Prvo izaberi vodnu granu iz liste.", parent=self)
            return
        try:
            branch = self._branch_from_form(self.water_selected_id)
            self._validate_branch_room(branch)
            self._water_registry().update_water_branch(branch.id, **branch.__dict__)
        except (KeyError, ValueError, TypeError) as exc:
            messagebox.showwarning("LAT-CES — Voda", str(exc), parent=self)
            return
        self._refresh_water_editor()
        self.status_var.set(f"Vodna grana izmijenjena: {branch.id}")
        self.refresh_view()

    def _delete_water(self) -> None:
        if not self.water_selected_id:
            return
        deleted = self._water_registry().remove_water_branch(self.water_selected_id)
        self.water_selected_id = None
        self._refresh_water_editor()
        self.status_var.set(f"Vodna grana obrisana: {deleted.id}")
        self.refresh_view()

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        if not hasattr(self, "water_list"):
            return
        for branch in self._water_registry().all_water_branches:
            x1, y1 = self.model_to_canvas(Point2D(branch.x1_m, branch.y1_m))
            x2, y2 = self.model_to_canvas(Point2D(branch.x2_m, branch.y2_m))
            self.canvas.create_line(x1, y1, x2, y2, fill="#2563eb", width=max(2, min(6, int(branch.diameter_m * 160))))
            self.canvas.create_oval(x1 - 4, y1 - 4, x1 + 4, y1 + 4, outline="#1d4ed8", width=2)
            self.canvas.create_oval(x2 - 4, y2 - 4, x2 + 4, y2 + 4, outline="#1d4ed8", width=2)
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10, text=f"{branch.service} · Ø{branch.diameter_m:.3f}", fill="#1d4ed8", font=("Segoe UI", 8, "bold"))
        if self.water_placing:
            self.canvas.create_text(20, 90, text="VODA — klikni početak, pa završetak grane", anchor="nw", fill="#1d4ed8", font=("Segoe UI", 10, "bold"))
            if self.water_start is not None:
                x, y = self.model_to_canvas(self.water_start)
                self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, outline="#1d4ed8", width=3)


def main() -> None:
    WaterMEPDraftingApp().mainloop()


if __name__ == "__main__":
    main()
