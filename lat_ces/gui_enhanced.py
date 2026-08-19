"""Enhanced Building Model editor layered on top of the existing LAT-CES GUI.

This module deliberately subclasses the existing GUI instead of replacing it.
It adds the missing interactive drafting workflow: dimension-linked floor-plan
resizing, draggable rooms/partitions/openings, explicit opening dimensions,
room dimension labels, and 3-D zoom.
"""
from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk

from lat_ces.gui import LATCESApp
from lat_ces.building.floor_plan import Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.model import Room


class EnhancedLATCESApp(LATCESApp):
    """Compatibility-preserving enhancement of the existing desktop GUI."""

    def __init__(self) -> None:
        self.zoom_3d = 1.0
        self.drag_payload: str | None = None
        self.room_name_var: tk.StringVar | None = None
        self.room_length_var: tk.StringVar | None = None
        self.room_width_var: tk.StringVar | None = None
        self.partition_length_var: tk.StringVar | None = None
        self.partition_thickness_var: tk.StringVar | None = None
        self.door_width_var: tk.StringVar | None = None
        self.door_height_var: tk.StringVar | None = None
        self.window_width_var: tk.StringVar | None = None
        self.window_height_var: tk.StringVar | None = None
        super().__init__()
        self.canvas.bind("<MouseWheel>", self._zoom_wheel, add="+")
        self.canvas.bind("<Button-4>", self._zoom_in_linux, add="+")
        self.canvas.bind("<Button-5>", self._zoom_out_linux, add="+")

    def _build_side_panel(self, side: ttk.Frame) -> None:
        super()._build_side_panel(side)
        palette = ttk.LabelFrame(side, text="Biblioteka — povuci na tlocrt", padding=8)
        palette.pack(fill="x", pady=(10, 0))

        room_box = ttk.LabelFrame(palette, text="Prostorija", padding=6)
        room_box.pack(fill="x", pady=(0, 6))
        self.room_name_var = tk.StringVar(value="Nova prostorija")
        self.room_length_var = tk.StringVar(value="4.00")
        self.room_width_var = tk.StringVar(value="3.00")
        self._field(room_box, "Naziv", self.room_name_var, 0)
        self._field(room_box, "Dužina (m)", self.room_length_var, 1)
        self._field(room_box, "Širina (m)", self.room_width_var, 2)
        self._drag_label(room_box, "▣  PROSTORIJA  — povuci", "room")

        partition_box = ttk.LabelFrame(palette, text="Pregradni zid", padding=6)
        partition_box.pack(fill="x", pady=6)
        self.partition_length_var = tk.StringVar(value="3.00")
        self.partition_thickness_var = tk.StringVar(value="0.12")
        self._field(partition_box, "Dužina (m)", self.partition_length_var, 0)
        self._field(partition_box, "Debljina (m)", self.partition_thickness_var, 1)
        self._drag_label(partition_box, "━  PREGRADNI ZID  — povuci", "partition")

        opening_box = ttk.LabelFrame(palette, text="Vrata / prozor", padding=6)
        opening_box.pack(fill="x", pady=6)
        self.door_width_var = tk.StringVar(value="0.90")
        self.door_height_var = tk.StringVar(value="2.10")
        self.window_width_var = tk.StringVar(value="1.20")
        self.window_height_var = tk.StringVar(value="1.20")
        self._field(opening_box, "Vrata širina", self.door_width_var, 0)
        self._field(opening_box, "Vrata visina", self.door_height_var, 1)
        self._field(opening_box, "Prozor širina", self.window_width_var, 2)
        self._field(opening_box, "Prozor visina", self.window_height_var, 3)
        row = ttk.Frame(opening_box)
        row.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self._drag_label(row, "🚪 VRATA — povuci na zid", "door")
        self._drag_label(row, "▣ PROZOR — povuci na zid", "window")

        hint = ttk.Label(palette, text="Otvor se hvata za najbliži zid.\nProstorije ostaju dimenzionalni objekti BuildingModela.", wraplength=315)
        hint.pack(anchor="w", pady=(4, 0))

        self.canvas.bind("<ButtonRelease-1>", self._drop_payload, add="+")

    @staticmethod
    def _field(parent: ttk.Frame, label: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        ttk.Entry(parent, textvariable=variable, width=12).grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
        parent.columnconfigure(1, weight=1)

    def _drag_label(self, parent: ttk.Widget, text: str, payload: str) -> None:
        label = ttk.Label(parent, text=text, relief="raised", padding=(5, 4), cursor="hand2")
        if parent.grid_slaves():
            # The field rows in room/partition/opening containers use grid.
            # Never mix pack and grid inside the same Tk container.
            next_row = max((int(child.grid_info().get("row", 0)) for child in parent.grid_slaves()), default=-1) + 1
            label.grid(row=next_row, column=0, columnspan=2, sticky="ew", padx=2, pady=2)
            parent.columnconfigure(0, weight=1)
            parent.columnconfigure(1, weight=1)
        else:
            # The dedicated button row is an otherwise empty frame, so pack is safe.
            label.pack(side="left", fill="x", expand=True, padx=2, pady=2)
        label.bind("<ButtonPress-1>", lambda _event, value=payload: self._start_payload(value))

    def _start_payload(self, payload: str) -> None:
        if self.view_step.get() != 3:
            self.view_step.set(3)
            self.goto_step()
        self.drag_payload = payload
        self.status_var.set(f"Povuci element '{payload}' na tlocrt.")

    def _drop_payload(self, event: tk.Event) -> None:
        payload = self.drag_payload
        self.drag_payload = None
        if not payload or self.view_step.get() != 3:
            return
        point = self.snap_point(self.canvas_to_model(event.x, event.y))
        try:
            if payload == "room":
                self._drop_room(point)
            elif payload == "partition":
                self._drop_partition(point)
            else:
                self._drop_opening(point, payload)
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Building Model", str(exc), parent=self)

    @staticmethod
    def snap_point(point: Point2D) -> Point2D:
        return Point2D(round(point.x * 10) / 10.0, round(point.y * 10) / 10.0)

    def _number(self, variable: tk.StringVar, label: str, minimum: float = 0.01) -> float:
        try:
            value = float(variable.get())
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} mora biti broj") from exc
        if value < minimum:
            raise ValueError(f"{label} mora biti ≥ {minimum:.2f} m")
        return value

    def _drop_room(self, point: Point2D) -> None:
        name = (self.room_name_var.get() if self.room_name_var else "Nova prostorija").strip() or "Prostorija"
        length = self._number(self.room_length_var, "Dužina prostorije")
        width = self._number(self.room_width_var, "Širina prostorije")
        level = self.active_level
        height = level.height
        max_x = level.length_m or max(self.plan_bounds()[1], length)
        max_y = level.width_m or max(self.plan_bounds()[3], width)
        x = min(max(point.x, 0.0), max(0.0, max_x - length))
        y = min(max(point.y, 0.0), max(0.0, max_y - width))
        room = Room(name=name, footprint=Box3D(Point3D(x, y, 0.0), length, width, height))
        level.add_room(room)
        self.status_var.set(f"Dodana prostorija: {name} · {length:.2f} × {width:.2f} m")
        self.refresh_view()

    def _drop_partition(self, point: Point2D) -> None:
        length = self._number(self.partition_length_var, "Dužina pregradnog zida")
        thickness = self._number(self.partition_thickness_var, "Debljina pregradnog zida")
        x0 = point.x - length / 2.0
        x1 = point.x + length / 2.0
        wall = Wall(
            name=f"Pregradni zid {self.floor_plan.wall_count + 1}",
            segment=Segment2D(Point2D(x0, point.y), Point2D(x1, point.y)),
            thickness=thickness,
        )
        self.floor_plan.add_wall(wall)
        self.editor.selected_wall_id = wall.wall_id
        self.status_var.set(f"Dodana pregrada · {length:.2f} × {thickness:.2f} m")
        self.refresh_view()

    def _drop_opening(self, point: Point2D, kind: str) -> None:
        wall = self.editor.nearest_wall(point)
        if wall is None:
            raise ValueError("Vrata/prozor se moraju spustiti na zid.")
        if kind == "door":
            width = self._number(self.door_width_var, "Širina vrata")
            height = self._number(self.door_height_var, "Visina vrata")
        else:
            width = self._number(self.window_width_var, "Širina prozora")
            height = self._number(self.window_height_var, "Visina prozora")
        length = wall.segment.length
        dx = wall.segment.end.x - wall.segment.start.x
        dy = wall.segment.end.y - wall.segment.start.y
        projection = ((point.x - wall.segment.start.x) * dx + (point.y - wall.segment.start.y) * dy) / (length * length)
        offset = min(max(0.0, projection * length - width / 2.0), max(0.0, length - width))
        wall.add_opening(Opening(kind=kind, offset=offset, width=width, height_m=height))
        self.status_var.set(f"{kind.capitalize()} dodano · {width:.2f} × {height:.2f} m")
        self.refresh_view()

    def apply_level_spec(self) -> None:
        """Apply level dimensions and scale the existing floor plan with them."""
        try:
            name = self.level_name_var.get().strip()
            height = float(self.height_var.get())
            new_length = float(self.level_length_var.get())
            new_width = float(self.level_width_var.get())
            if not name or height <= 0 or new_length <= 0 or new_width <= 0:
                raise ValueError("Naziv i dimenzije etaže moraju biti pozitivne")
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Etaža", str(exc), parent=self)
            return

        level = self.active_level
        old_length = level.length_m or max(self.plan_bounds()[1], 1.0)
        old_width = level.width_m or max(self.plan_bounds()[3], 1.0)
        sx = new_length / old_length
        sy = new_width / old_width
        plan = level.floor_plan
        if plan is not None:
            for wall in plan.walls.values():
                start, end = wall.segment.start, wall.segment.end
                old_wall_length = wall.segment.length
                new_start = Point2D(start.x * sx, start.y * sy)
                new_end = Point2D(end.x * sx, end.y * sy)
                wall.segment = Segment2D(new_start, new_end)
                ratio = wall.segment.length / old_wall_length if old_wall_length else 1.0
                wall.openings = [
                    Opening(kind=o.kind, offset=o.offset * ratio, width=o.width * ratio, height_m=o.height_m)
                    for o in wall.openings
                ]
        for room in level.rooms.values():
            fp = room.footprint
            room.footprint = Box3D(Point3D(fp.origin.x * sx, fp.origin.y * sy, fp.origin.z), fp.length * sx, fp.width * sy, fp.height)
        level.name = name
        level.height = height
        level.length_m = new_length
        level.width_m = new_width
        if plan is not None:
            plan.name = name
        self.status_var.set(f"Etaža + tlocrt dimenzionirani: {new_length:.2f} × {new_width:.2f} × {height:.2f} m")
        self.refresh_view()

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        for room in self.active_level.rooms.values():
            p = room.footprint.origin
            q = room.footprint.max_point
            x1, y1 = self.model_to_canvas(Point2D(p.x, p.y))
            x2, y2 = self.model_to_canvas(Point2D(q.x, q.y))
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#0f766e", dash=(5, 3), width=2)
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            self.canvas.create_text(cx, cy, text=f"{room.name}\n{room.footprint.length:.2f} × {room.footprint.width:.2f} m", fill="#0f766e", font=("Segoe UI", 9, "bold"))
        self.canvas.create_text(20, 42, text="Dimenzije prostorija su vezane za BuildingModel", anchor="nw", fill="#0f766e", font=("Segoe UI", 9))

    def project_3d(self, x: float, y: float, z: float, scale: float, width: float, height: float) -> tuple[float, float]:
        return super().project_3d(x, y, z, scale * self.zoom_3d, width, height)

    def _zoom_wheel(self, event: tk.Event) -> None:
        if self.view_step.get() != 5:
            return
        delta = 1.10 if event.delta > 0 else 1.0 / 1.10
        self.zoom_3d = min(4.0, max(0.25, self.zoom_3d * delta))
        self.status_var.set(f"3D zum: {self.zoom_3d:.2f}×")
        self.redraw_active_view()

    def _zoom_in_linux(self, _event: tk.Event) -> None:
        if self.view_step.get() == 5:
            self.zoom_3d = min(4.0, self.zoom_3d * 1.10)
            self.redraw_active_view()

    def _zoom_out_linux(self, _event: tk.Event) -> None:
        if self.view_step.get() == 5:
            self.zoom_3d = max(0.25, self.zoom_3d / 1.10)
            self.redraw_active_view()

    def goto_step(self) -> None:
        super().goto_step()
        if self.view_step.get() != 5:
            self.zoom_3d = 1.0


def main() -> None:
    EnhancedLATCESApp().mainloop()


if __name__ == "__main__":
    main()
