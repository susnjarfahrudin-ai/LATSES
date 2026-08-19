"""Live dimensioned drafting layer for the LAT-CES Building Model editor."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from lat_ces.building.floor_plan import Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building.geometry3d import build_geometry
from lat_ces.building.model import Level
from lat_ces.building.orientation import ViewStyle
from lat_ces.building.workflow import make_envelope_floor_plan
from lat_ces.gui_enhanced import EnhancedLATCESApp


class DraftingLATCESApp(EnhancedLATCESApp):
    """Dimension-first drafting: create, preview, place and measure elements."""

    def __init__(self) -> None:
        # Do not create Tk variables here: EnhancedLATCESApp/LATCESApp has not
        # created the root window yet.  Tk variables are initialized in
        # _build_side_panel(), which runs after the root exists.
        self.wall_drafting = False
        self.wall_preview_id: int | None = None
        self.wall_draft_length = 3.0
        self.wall_draft_thickness = 0.20
        self.wall_draft_start: Point2D | None = None
        super().__init__()
        self.canvas.unbind("<Button-1>")
        self.canvas.bind("<Button-1>", self._draft_click)
        self.canvas.bind("<Motion>", self._draft_motion, add="+")

    def _build_side_panel(self, side: ttk.Frame) -> None:
        # LATCESApp creates the Tk root before this hook is called, so this is
        # the first safe place to construct these StringVars.
        self.wall_length_var = tk.StringVar(master=self, value="3.00")
        self.wall_thickness_var = tk.StringVar(master=self, value="0.20")
        super()._build_side_panel(side)
        box = ttk.LabelFrame(side, text="Dodaj novi zid", padding=8)
        box.pack(fill="x", pady=(10, 0))
        self.wall_editor = ttk.Frame(box)
        self.wall_editor.pack(fill="x")
        ttk.Button(box, text="＋ Dodaj novi zid", command=self._open_wall_editor).pack(fill="x")
        self.wall_fields = ttk.Frame(box)
        self.wall_fields.pack(fill="x", pady=(6, 0))
        self._field(self.wall_fields, "Dužina (m)", self.wall_length_var, 0)
        self._field(self.wall_fields, "Debljina (m)", self.wall_thickness_var, 1)
        ttk.Button(self.wall_fields, text="Kreiraj zid", command=self._create_wall_preview).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        ttk.Label(box, text="Nakon 'Kreiraj zid' linija prati miš. Klikom je postavljaš na željeno mjesto.", wraplength=315).pack(anchor="w", pady=(6, 0))
        self.wall_fields.pack_forget()

    def configure_stage(self, step: int) -> None:
        super().configure_stage(step)
        if step != 2:
            return
        levels = list(self.workflow.model.levels.values())
        if not levels:
            return
        is_ground = levels[0].level_id == self.active_level.level_id
        if is_ground:
            self.level_length_var.set("10.00")
            self.level_width_var.set("10.00")
        for child in self.stage_controls.winfo_children():
            row = str(child.grid_info().get("row", ""))
            if row in {"2", "3"} and child.winfo_class() == "TEntry":
                child.configure(state="disabled" if is_ground else "normal")

    @staticmethod
    def _is_default_envelope(plan) -> bool:
        return bool(plan) and plan.wall_count == 4 and all(
            wall.name.startswith("Vanjski zid") and not wall.openings
            for wall in plan.walls.values()
        )

    def apply_level_spec(self) -> None:
        """Apply level dimensions without collapsing rectangular floors to squares."""
        try:
            name = self.level_name_var.get().strip()
            height = float(self.height_var.get())
            length = float(self.level_length_var.get())
            width = float(self.level_width_var.get())
            if not name or height <= 0 or length <= 0 or width <= 0:
                raise ValueError("Naziv i dimenzije etaže moraju biti pozitivne")
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Etaža", str(exc), parent=self)
            return

        levels = list(self.workflow.model.levels.values())
        level = self.active_level
        if levels and levels[0].level_id == level.level_id:
            length = width = 10.0
            self.level_length_var.set("10.00")
            self.level_width_var.set("10.00")

        old_length = level.length_m or 10.0
        old_width = level.width_m or 10.0
        plan = level.floor_plan
        if plan is None or self._is_default_envelope(plan):
            level.set_floor_plan(make_envelope_floor_plan(name, length, width, 0.20))
        else:
            sx = length / old_length if old_length else 1.0
            sy = width / old_width if old_width else 1.0
            for wall in plan.walls.values():
                start, end = wall.segment.start, wall.segment.end
                old_wall_length = wall.segment.length
                wall.segment = Segment2D(
                    Point2D(start.x * sx, start.y * sy),
                    Point2D(end.x * sx, end.y * sy),
                )
                ratio = wall.segment.length / old_wall_length if old_wall_length else 1.0
                wall.openings = [
                    Opening(
                        kind=o.kind,
                        offset=o.offset * ratio,
                        width=o.width * ratio,
                        height_m=o.height_m,
                    )
                    for o in wall.openings
                ]
            for room in level.rooms.values():
                fp = room.footprint
                room.footprint = Box3D(
                    Point3D(fp.origin.x * sx, fp.origin.y * sy, fp.origin.z),
                    fp.length * sx,
                    fp.width * sy,
                    fp.height,
                )
            plan.name = name

        level.name = name
        level.height = height
        level.length_m = length
        level.width_m = width
        self.status_var.set(f"Etaža primijenjena: {name} · {length:.2f} × {width:.2f} × {height:.2f} m")
        self.refresh_view()

    def apply_roof(self) -> None:
        """The roof follows the fixed 10 × 10 building envelope."""
        self.level_length_var.set("10.00")
        self.level_width_var.set("10.00")
        super().apply_roof()

    def _open_wall_editor(self) -> None:
        self.wall_fields.pack(fill="x", pady=(6, 0))
        self.status_var.set("Unesi dužinu i debljinu, zatim klikni 'Kreiraj zid'.")
        self.view_step.set(3)
        self.goto_step()

    def _create_wall_preview(self) -> None:
        try:
            length = float(self.wall_length_var.get())
            thickness = float(self.wall_thickness_var.get())
            if length <= 0 or thickness <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("LAT-CES — Zid", "Dužina i debljina zida moraju biti pozitivne.", parent=self)
            return
        self.wall_draft_length = length
        self.wall_draft_thickness = thickness
        self.wall_drafting = True
        self.wall_draft_start = None
        self.editor.set_tool("select")
        self.status_var.set(f"Zid {length:.2f} × {thickness:.2f} m — pomjeraj miš; klik postavlja zid.")
        self.redraw_active_view()

    def _draft_motion(self, event: tk.Event) -> None:
        if not self.wall_drafting or self.view_step.get() != 3:
            return
        point = self.snap_point(self.canvas_to_model(event.x, event.y))
        half = self.wall_draft_length / 2.0
        start = Point2D(point.x - half, point.y)
        end = Point2D(point.x + half, point.y)
        if self.wall_preview_id is not None:
            self.canvas.delete(self.wall_preview_id)
        x1, y1 = self.model_to_canvas(start)
        x2, y2 = self.model_to_canvas(end)
        self.wall_preview_id = self.canvas.create_line(x1, y1, x2, y2, fill="#2563eb", width=4, dash=(8, 4))
        self._draw_live_distances(point, start, end)

    def _draft_click(self, event: tk.Event) -> None:
        if self.wall_drafting and self.view_step.get() == 3:
            point = self.snap_point(self.canvas_to_model(event.x, event.y))
            half = self.wall_draft_length / 2.0
            start = Point2D(point.x - half, point.y)
            end = Point2D(point.x + half, point.y)
            wall = Wall(
                name=f"Zid {self.floor_plan.wall_count + 1}",
                segment=Segment2D(start, end),
                thickness=self.wall_draft_thickness,
            )
            self.floor_plan.add_wall(wall)
            self.editor.selected_wall_id = wall.wall_id
            self.wall_drafting = False
            self.wall_draft_start = point
            self.status_var.set(f"Postavljen zid: {self.wall_draft_length:.2f} × {self.wall_draft_thickness:.2f} m")
            self.refresh_view()
            return
        self.editor.click(event)

    def _external_bounds(self) -> tuple[float, float, float, float]:
        level = self.active_level
        return 0.0, max(level.length_m, 0.0), 0.0, max(level.width_m, 0.0)

    def _draw_live_distances(self, point: Point2D, start: Point2D, end: Point2D) -> None:
        self.canvas.delete("live-dimension")
        xmin, xmax, ymin, ymax = self._external_bounds()
        if xmax <= xmin or ymax <= ymin:
            return
        left = max(0.0, start.x - xmin)
        right = max(0.0, xmax - end.x)
        bottom = max(0.0, point.y - ymin)
        top = max(0.0, ymax - point.y)
        x1, y1 = self.model_to_canvas(start)
        x2, y2 = self.model_to_canvas(end)
        cx, cy = self.model_to_canvas(point)
        self.canvas.create_text(x1, y1 - 18, text=f"← {left:.2f} m", fill="#b45309", tags="live-dimension", anchor="e")
        self.canvas.create_text(x2, y2 - 18, text=f"{right:.2f} m →", fill="#b45309", tags="live-dimension", anchor="w")
        self.canvas.create_text(cx + 12, cy, text=f"↓ {bottom:.2f} m   ↑ {top:.2f} m", fill="#b45309", tags="live-dimension", anchor="w")
        self.canvas.create_text(cx, cy + 22, text=f"Zid {self.wall_draft_length:.2f} × {self.wall_draft_thickness:.2f} m", fill="#1d4ed8", tags="live-dimension")

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        if self.wall_drafting:
            self.canvas.create_text(20, 20, text="PREVIEW ZIDA — pomjeraj miš i klikni za postavljanje", anchor="nw", fill="#1d4ed8", font=("Segoe UI", 10, "bold"), tags="live-dimension")

    def _draw_3d_wall_face(self, wall, z0: float, scale: float, width: float, height: float, style: ViewStyle) -> None:
        """Render the wall as solid faces around opening voids."""
        openings = sorted(wall.openings, key=lambda item: item.offset)
        cursor = 0.0
        dx = wall.x2 - wall.x1
        dy = wall.y2 - wall.y1
        length = wall.length
        if length <= 0:
            return

        def point_at(distance: float, z: float) -> tuple[float, float]:
            t = distance / length
            return self.project_3d(wall.x1 + dx * t, wall.y1 + dy * t, z, scale, width, height)

        def face(d0: float, d1: float, za: float, zb: float) -> None:
            if d1 <= d0 or zb <= za:
                return
            p0 = point_at(d0, za)
            p1 = point_at(d1, za)
            p2 = point_at(d1, zb)
            p3 = point_at(d0, zb)
            if style is ViewStyle.CONSTRUCTIONAL_LINE:
                for a, b in ((p0, p1), (p1, p2), (p2, p3), (p3, p0)):
                    self.canvas.create_line(*a, *b, fill="#374151", width=2)
            else:
                self.canvas.create_polygon(*p0, *p1, *p2, *p3, fill="#d8c8ad", outline="#6b5b4b")

        for opening in openings:
            start = max(0.0, min(length, opening.offset))
            end = max(start, min(length, opening.offset + opening.width))
            face(cursor, start, z0, z0 + wall.height)
            face(start, end, z0 + opening.height_m, z0 + wall.height)
            cursor = end
        face(cursor, length, z0, z0 + wall.height)

    def draw_3d(self) -> None:
        self.canvas.delete("all")
        geometries = build_geometry(self.workflow.model)
        width, height = max(self.canvas.winfo_width(), 500), max(self.canvas.winfo_height(), 350)
        style = ViewStyle(self.view_style_var.get())
        scale = 24.0
        for idx, geometry in enumerate(geometries):
            z0 = sum(g.height for g in geometries[:idx])
            for wall in geometry.walls:
                self._draw_3d_wall_face(wall, z0, scale, width, height, style)
        roof = self.workflow.model.roof
        if roof and roof.height_m > 0 and geometries:
            top = sum(g.height for g in geometries)
            corners = ((0.0, 0.0, top), (roof.length_m, 0.0, top), (roof.length_m, roof.width_m, top), (0.0, roof.width_m, top))
            pts = [self.project_3d(x, y, z, scale, width, height) for x, y, z in corners]
            peak = self.project_3d(roof.length_m / 2.0, roof.width_m / 2.0, top + roof.height_m, scale, width, height)
            if style is ViewStyle.CONSTRUCTIONAL_LINE:
                for i in range(4):
                    self.canvas.create_line(*pts[i], *pts[(i + 1) % 4], fill="#7c3aed", width=2)
                    self.canvas.create_line(*pts[i], *peak, fill="#7c3aed", width=2)
            else:
                fills = ("#a9b4c2", "#8f9cac", "#7e8998", "#95a0ae")
                for i, fill in enumerate(fills):
                    self.canvas.create_polygon(*pts[i], *pts[(i + 1) % 4], *peak, fill=fill, outline="#667085")
        title = "3D LINIJSKI" if style is ViewStyle.CONSTRUCTIONAL_LINE else "PRIRODNI 3D"
        self.canvas.create_text(20, 20, text=f"{title} · otvori izvedeni iz BuildingModela", anchor="nw", fill="#374151", font=("Segoe UI", 12, "bold"))
        self.draw_compass()

    def _drop_opening(self, point: Point2D, kind: str) -> None:
        super()._drop_opening(point, kind)


def main() -> None:
    DraftingLATCESApp().mainloop()


if __name__ == "__main__":
    main()
