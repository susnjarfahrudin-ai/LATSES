"""LAT-CES Building-first desktop application.

One BuildingModel is the source of truth for roof, levels, floor plans,
sections and 3-D views.  The GUI only renders and edits that model.
"""
from __future__ import annotations

import json
import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from lat_ces.application.service import analyze_config, export_report, load_config
from lat_ces.building.floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from lat_ces.building.geometry3d import build_geometry
from lat_ces.building.model import BuildingModel, Level
from lat_ces.building.orientation import BuildingOrientation, ViewStyle
from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.section import SectionAxis, SectionDefinition, SectionView
from lat_ces.building.workflow import BuildingWorkflow, make_square_floor_plan

STEPS = ((1, "Krov"), (2, "Sprat"), (3, "Tlocrt"), (4, "Presjek"), (5, "3D"))
EDITOR_TOOLS = (("select", "Izaberi"), ("draw", "Nova linija / zid"), ("move", "Pomjeri"), ("delete", "Obriši"), ("door", "Vrata"), ("window", "Prozor"))


class FloorPlanEditor:
    def __init__(self, app: "LATCESApp") -> None:
        self.app = app
        self.tool = "select"
        self.start_point: Point2D | None = None
        self.selected_wall_id: str | None = None
        self.drag_last: Point2D | None = None

    @property
    def floor_plan(self) -> FloorPlan:
        return self.app.workflow.floor_plan

    @staticmethod
    def snap(point: Point2D) -> Point2D:
        return Point2D(round(point.x * 10) / 10.0, round(point.y * 10) / 10.0)

    @staticmethod
    def point_segment_distance(point: Point2D, start: Point2D, end: Point2D) -> float:
        dx, dy = end.x - start.x, end.y - start.y
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return math.hypot(point.x - start.x, point.y - start.y)
        t = max(0.0, min(1.0, ((point.x - start.x) * dx + (point.y - start.y) * dy) / length_sq))
        px, py = start.x + t * dx, start.y + t * dy
        return math.hypot(point.x - px, point.y - py)

    def nearest_wall(self, point: Point2D, tolerance_m: float = 0.30) -> Wall | None:
        best: tuple[float, Wall] | None = None
        for wall in self.floor_plan.walls.values():
            distance = self.point_segment_distance(point, wall.segment.start, wall.segment.end)
            if distance <= tolerance_m and (best is None or distance < best[0]):
                best = (distance, wall)
        return best[1] if best else None

    def set_tool(self, tool: str) -> None:
        self.tool = tool
        self.start_point = None
        self.drag_last = None
        self.app.tool_var.set(tool)
        self.app.status_var.set(f"Alat: {dict(EDITOR_TOOLS)[tool]}")
        self.app.redraw_active_view()

    def click(self, event: tk.Event) -> None:
        if self.app.view_step.get() != 3:
            return
        point = self.snap(self.app.canvas_to_model(event.x, event.y))
        if self.tool == "draw":
            if self.start_point is None:
                self.start_point = point
                self.app.status_var.set(f"Početak zida: ({point.x:.1f}, {point.y:.1f}) m — klikni kraj")
                return
            dx = point.x - self.start_point.x
            dy = point.y - self.start_point.y
            if math.hypot(dx, dy) < 0.1:
                return
            reference = self.nearest_wall(self.start_point, tolerance_m=2.0)
            if reference is not None and reference.segment.length > 0:
                angle = math.atan2(reference.segment.end.y - reference.segment.start.y, reference.segment.end.x - reference.segment.start.x)
                candidate_angles = (angle, angle + math.pi / 2.0)
                best = max(candidate_angles, key=lambda a: abs(dx * math.cos(a) + dy * math.sin(a)))
                distance = math.hypot(dx, dy)
                point = Point2D(self.start_point.x + distance * math.cos(best), self.start_point.y + distance * math.sin(best))
            elif abs(dx) >= abs(dy):
                point = Point2D(point.x, self.start_point.y)
            else:
                point = Point2D(self.start_point.x, point.y)
            wall = Wall(name=f"Zid {self.floor_plan.wall_count + 1}", segment=Segment2D(self.start_point, point), thickness=0.20)
            self.floor_plan.add_wall(wall)
            self.start_point = None
            self.selected_wall_id = wall.wall_id
        else:
            wall = self.nearest_wall(point)
            if wall is None:
                self.selected_wall_id = None
                self.app.update_selected_wall()
                self.app.redraw_active_view()
                return
            self.selected_wall_id = wall.wall_id
            if self.tool == "delete":
                del self.floor_plan.walls[wall.wall_id]
                self.selected_wall_id = None
            elif self.tool in {"door", "window"}:
                self.add_opening(wall, point, self.tool)
            else:
                self.app.status_var.set(f"Izabran: {wall.name} — {wall.segment.length:.2f} m")
        self.app.refresh_view()

    def begin_drag(self, event: tk.Event) -> None:
        if self.app.view_step.get() != 3 or self.tool != "move":
            return
        point = self.snap(self.app.canvas_to_model(event.x, event.y))
        wall = self.nearest_wall(point)
        if wall is not None:
            self.selected_wall_id, self.drag_last = wall.wall_id, point

    def drag(self, event: tk.Event) -> None:
        if self.app.view_step.get() != 3 or self.tool != "move" or self.selected_wall_id is None or self.drag_last is None:
            return
        wall = self.floor_plan.walls.get(self.selected_wall_id)
        if wall is None:
            return
        point = self.snap(self.app.canvas_to_model(event.x, event.y))
        dx, dy = point.x - self.drag_last.x, point.y - self.drag_last.y
        wall.segment = Segment2D(Point2D(wall.segment.start.x + dx, wall.segment.start.y + dy), Point2D(wall.segment.end.x + dx, wall.segment.end.y + dy))
        self.drag_last = point
        self.app.refresh_view()

    def end_drag(self, _event: tk.Event) -> None:
        self.drag_last = None

    def add_opening(self, wall: Wall, point: Point2D, kind: str) -> None:
        length = wall.segment.length
        dx, dy = wall.segment.end.x - wall.segment.start.x, wall.segment.end.y - wall.segment.start.y
        projection = ((point.x - wall.segment.start.x) * dx + (point.y - wall.segment.start.y) * dy) / (length * length)
        offset = max(0.0, min(length, projection * length))
        default_width = 0.90 if kind == "door" else 1.20
        width = simpledialog.askfloat("Otvor", f"Širina {kind} (m):", initialvalue=default_width, minvalue=0.10, parent=self.app)
        if width is None:
            return
        offset = min(max(0.0, offset - width / 2.0), max(0.0, length - width))
        try:
            wall.add_opening(Opening(kind=kind, offset=offset, width=width))
        except ValueError as exc:
            messagebox.showwarning("LAT-CES", str(exc), parent=self.app)


class LATCESApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("LAT-CES — Building Model")
        self.geometry("1440x900")
        self.minsize(1180, 760)
        self.workflow = self.new_workflow()
        self.view_step = tk.IntVar(value=1)
        self.active_mode = tk.StringVar(value="Projektovanje")
        self.tool_var = tk.StringVar(value="select")
        self.height_var = tk.StringVar(value="2.80")
        self.level_length_var = tk.StringVar(value="10.00")
        self.level_width_var = tk.StringVar(value="10.00")
        self.roof_type_var = tk.StringVar(value="Četverovodni")
        self.roof_construction_var = tk.StringVar(value="Drvena konstrukcija")
        self.roof_covering_var = tk.StringVar(value="Crijep")
        self.roof_substructure_var = tk.StringVar(value="Letve + kontra-letve")
        self.roof_support_var = tk.StringVar(value="Krovna ploča / vijenci")
        self.roof_slope_var = tk.StringVar(value="25.0")
        self.roof_height_var = tk.StringVar(value="2.50")
        self.orientation_var = tk.StringVar(value="0.0")
        self.section_axis_var = tk.StringVar(value="X")
        self.section_position_var = tk.StringVar(value="5.0")
        self.view_style_var = tk.StringVar(value=ViewStyle.CONSTRUCTIONAL_LINE.value)
        self.model_path = tk.StringVar()
        self.status_var = tk.StringVar(value="LAT-CES — Building-first interfejs")
        self.selected_length_var = tk.StringVar(value="—")
        self.selected_thickness_var = tk.StringVar(value="0.20")
        self.editor = FloorPlanEditor(self)
        self._build_ui()
        self.apply_default_orientation()
        self.configure_stage(1)
        self.refresh_view()

    @staticmethod
    def new_workflow() -> BuildingWorkflow:
        model = BuildingModel(name="Novi objekat")
        workflow = BuildingWorkflow(model=model)
        workflow.set_floor_plan(make_square_floor_plan("Prizemlje", 10.0))
        return workflow

    def apply_default_orientation(self) -> None:
        if getattr(self.workflow.model, "orientation", None) is None:
            self.workflow.model.set_orientation(BuildingOrientation(north_azimuth_deg=float(self.orientation_var.get())))
        else:
            self.orientation_var.set(f"{self.workflow.model.orientation.north_azimuth_deg:.1f}")

    @property
    def floor_plan(self) -> FloorPlan:
        return self.workflow.floor_plan

    @property
    def active_level(self) -> Level:
        return self.workflow.active_level

    def _build_ui(self) -> None:
        header = ttk.Frame(self, padding=(18, 12))
        header.pack(fill="x")
        ttk.Label(header, text="LAT-CES", font=("Segoe UI", 22, "bold")).pack(side="left")
        ttk.Label(header, text="Building Model · Structural / Natural Views", font=("Segoe UI", 10)).pack(side="left", padx=(14, 0), pady=(7, 0))
        ttk.Button(header, text="Učitaj", command=self.load_project).pack(side="right")
        ttk.Button(header, text="Sačuvaj", command=self.save_project).pack(side="right", padx=7)
        ttk.Button(header, text="Novi", command=self.new_project).pack(side="right")

        steps = ttk.Frame(self, padding=(18, 0, 18, 10))
        steps.pack(fill="x")
        for number, title in STEPS:
            ttk.Radiobutton(steps, text=f"{number}. {title}", value=number, variable=self.view_step, command=self.goto_step).pack(side="left", padx=(0, 16))

        body = ttk.Frame(self, padding=(18, 0, 18, 12))
        body.pack(fill="both", expand=True)
        self.workspace = ttk.LabelFrame(body, text="LAT-CES", padding=8)
        self.workspace.pack(side="left", fill="both", expand=True)
        toolbar = ttk.Frame(self.workspace)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Label(toolbar, text="Etaža:").pack(side="left")
        self.level_var = tk.StringVar()
        self.level_box = ttk.Combobox(toolbar, textvariable=self.level_var, state="readonly", width=18)
        self.level_box.pack(side="left", padx=6)
        self.level_box.bind("<<ComboboxSelected>>", self.select_level_from_combo)
        ttk.Label(toolbar, text="|  Alati:").pack(side="left", padx=(10, 0))
        for tool, label in EDITOR_TOOLS:
            ttk.Radiobutton(toolbar, text=label, value=tool, variable=self.tool_var, command=lambda value=tool: self.editor.set_tool(value)).pack(side="left", padx=(5, 0))
        self.canvas = tk.Canvas(self.workspace, background="white", highlightthickness=1, highlightbackground="#cfd4da")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda _event: self.redraw_active_view())
        self.canvas.bind("<Button-1>", self.editor.click)
        self.canvas.bind("<ButtonPress-1>", self.editor.begin_drag)
        self.canvas.bind("<B1-Motion>", self.editor.drag)
        self.canvas.bind("<ButtonRelease-1>", self.editor.end_drag)

        side = ttk.Frame(body, width=320)
        side.pack(side="left", fill="y", padx=(14, 0))
        side.pack_propagate(False)
        self._build_side_panel(side)
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

    def _build_side_panel(self, side: ttk.Frame) -> None:
        nav = ttk.LabelFrame(side, text="Prikaz / faza", padding=10)
        nav.pack(fill="x")
        for text in ("Krov", "Sprat", "Tlocrt", "Presjek", "3D"):
            ttk.Button(nav, text=text, command=lambda value=text: self.jump_to_label(value)).pack(fill="x", pady=2)
        stage = ttk.LabelFrame(side, text="Trenutna faza", padding=10)
        stage.pack(fill="x", pady=(10, 0))
        self.stage_title = ttk.Label(stage, text="Krov", font=("Segoe UI", 14, "bold"))
        self.stage_title.pack(anchor="w")
        self.stage_info = ttk.Label(stage, wraplength=320)
        self.stage_info.pack(anchor="w", pady=(4, 8))
        self.stage_controls = ttk.Frame(stage)
        self.stage_controls.pack(fill="x")

        orientation = ttk.LabelFrame(side, text="Orijentacija objekta", padding=10)
        orientation.pack(fill="x", pady=(10, 0))
        ttk.Label(orientation, text="Sjeverni azimut (°)").grid(row=0, column=0, sticky="w")
        ttk.Entry(orientation, textvariable=self.orientation_var, width=12).grid(row=0, column=1, padx=(8, 0))
        ttk.Button(orientation, text="Primijeni", command=self.apply_orientation).grid(row=0, column=2, padx=(8, 0))
        self.orientation_info = ttk.Label(orientation, wraplength=320)
        self.orientation_info.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        selected = ttk.LabelFrame(side, text="Odabrani zid", padding=10)
        selected.pack(fill="x", pady=(10, 0))
        ttk.Label(selected, text="Dužina (m)").grid(row=0, column=0, sticky="w")
        ttk.Entry(selected, textvariable=self.selected_length_var).grid(row=0, column=1, sticky="ew", padx=(8, 0))
        ttk.Label(selected, text="Debljina (m)").grid(row=1, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(selected, textvariable=self.selected_thickness_var).grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(6, 0))
        ttk.Button(selected, text="Primijeni dimenzije", command=self.apply_wall_dimensions).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        selected.columnconfigure(1, weight=1)

        model_box = ttk.LabelFrame(side, text="Building Model", padding=10)
        model_box.pack(fill="x", pady=(10, 0))
        self.summary_text = tk.Text(model_box, height=9, width=40, wrap="word", state="disabled")
        self.summary_text.pack(fill="x")
        tools = ttk.LabelFrame(side, text="LAT-CES alati", padding=10)
        tools.pack(fill="x", pady=(10, 0))
        ttk.Button(tools, text="Provjeri model", command=self.validate_model).pack(fill="x")
        ttk.Button(tools, text="Scientific Analysis", command=self.open_analysis).pack(fill="x", pady=4)
        ttk.Button(tools, text="Sačuvaj konfiguraciju", command=self.save_project).pack(fill="x")

    def jump_to_label(self, label: str) -> None:
        self.view_step.set({title: number for number, title in STEPS}[label])
        self.goto_step()

    def configure_stage(self, step: int) -> None:
        for child in self.stage_controls.winfo_children():
            child.destroy()
        self.stage_title.configure(text=dict(STEPS)[step])
        if step == 1:
            self.workspace.configure(text="Krov")
            self.stage_info.configure(text="Definiši krov kao dio Building Modela: tip, konstrukcija, pokrov, oslonac, dimenzije, nagib i visinu.")
            fields = (("Vrsta", self.roof_type_var), ("Konstrukcija", self.roof_construction_var), ("Pokrov", self.roof_covering_var), ("Podkonstrukcija", self.roof_substructure_var), ("Oslonac", self.roof_support_var), ("Nagib (°)", self.roof_slope_var), ("Visina (m)", self.roof_height_var))
            for row, (label, var) in enumerate(fields):
                ttk.Label(self.stage_controls, text=label).grid(row=row, column=0, sticky="w", pady=2)
                ttk.Entry(self.stage_controls, textvariable=var, width=24).grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
            ttk.Button(self.stage_controls, text="Primijeni krov", command=self.apply_roof).grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(7, 0))
            self.stage_controls.columnconfigure(1, weight=1)
        elif step == 2:
            self.workspace.configure(text="Sprat / etaža")
            self.stage_info.configure(text="Etaža definiše naziv, visinu, tlocrtni gabarit, zidnu konstrukciju, izolaciju, obloge i stolariju.")
            self.level_name_var = tk.StringVar(value=self.active_level.name)
            fields = (("Naziv", self.level_name_var), ("Visina (m)", self.height_var), ("Dužina (m)", self.level_length_var), ("Širina (m)", self.level_width_var))
            for row, (label, var) in enumerate(fields):
                ttk.Label(self.stage_controls, text=label).grid(row=row, column=0, sticky="w", pady=2)
                ttk.Entry(self.stage_controls, textvariable=var).grid(row=row, column=1, sticky="ew", padx=(8, 0), pady=2)
            ttk.Button(self.stage_controls, text="Primijeni etažu", command=self.apply_level_spec).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(6, 2))
            ttk.Button(self.stage_controls, text="Dodaj novu etažu", command=self.add_level).grid(row=5, column=0, columnspan=2, sticky="ew")
            self.stage_controls.columnconfigure(1, weight=1)
        elif step == 3:
            self.workspace.configure(text=f"Tlocrt — {self.active_level.name}")
            self.stage_info.configure(text="Dimenzionalni tlocrt je geometrijska osnova za Presjek i 3D. Koristi samo jedan FloorPlan izvora.")
            for label, tool in (("Nova pregrada / zid", "draw"), ("Vrata", "door"), ("Prozor", "window")):
                ttk.Button(self.stage_controls, text=label, command=lambda value=tool: self.editor.set_tool(value)).pack(fill="x", pady=2)
        elif step == 4:
            self.workspace.configure(text="Presjek")
            self.stage_info.configure(text="Presjek je izveden iz istog Building Modela. Prikaz: konstrukcijski linijski ili prirodni.")
            row = ttk.Frame(self.stage_controls)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text="Pravac:").pack(side="left")
            ttk.Combobox(row, textvariable=self.section_axis_var, state="readonly", values=("X", "Y"), width=5).pack(side="left", padx=8)
            ttk.Label(row, text="Položaj (m):").pack(side="left")
            ttk.Entry(row, textvariable=self.section_position_var, width=8).pack(side="left", padx=6)
            ttk.Label(self.stage_controls, text="Stil:").pack(anchor="w", pady=(6, 2))
            ttk.Radiobutton(self.stage_controls, text="Konstrukcijski linijski", value=ViewStyle.CONSTRUCTIONAL_LINE.value, variable=self.view_style_var, command=self.redraw_active_view).pack(anchor="w")
            ttk.Radiobutton(self.stage_controls, text="Prirodni", value=ViewStyle.NATURAL.value, variable=self.view_style_var, command=self.redraw_active_view).pack(anchor="w")
        else:
            self.workspace.configure(text="3D Building Model")
            self.stage_info.configure(text="3D se generiše iz svih etaža i krovnog modela. Može biti konstrukcijski linijski ili prirodni.")
            ttk.Radiobutton(self.stage_controls, text="3D linijski", value=ViewStyle.CONSTRUCTIONAL_LINE.value, variable=self.view_style_var, command=self.redraw_active_view).pack(anchor="w")
            ttk.Radiobutton(self.stage_controls, text="Prirodni 3D", value=ViewStyle.NATURAL.value, variable=self.view_style_var, command=self.redraw_active_view).pack(anchor="w")

    def goto_step(self) -> None:
        step = self.view_step.get()
        self.workflow.current_step = step
        if step == 2:
            self.refresh_level_fields()
        self.configure_stage(step)
        self.refresh_view()

    def refresh_level_fields(self) -> None:
        self.height_var.set(f"{self.active_level.height:.2f}")
        self.level_length_var.set(f"{self.active_level.length_m or 10.0:.2f}")
        self.level_width_var.set(f"{self.active_level.width_m or 10.0:.2f}")

    def refresh_level_combo(self) -> None:
        levels = list(self.workflow.model.levels.values())
        self.level_box["values"] = [f"{idx + 1}. {level.name}" for idx, level in enumerate(levels)]
        active_index = next((idx for idx, level in enumerate(levels) if level.level_id == self.workflow.active_level_id), 0)
        if levels:
            self.level_box.current(active_index)
        self.refresh_level_fields()

    def select_level_from_combo(self, _event: tk.Event) -> None:
        index = self.level_box.current()
        levels = list(self.workflow.model.levels.values())
        if 0 <= index < len(levels):
            self.workflow.set_active_level(levels[index].level_id)
            self.editor.selected_wall_id = None
            self.refresh_level_fields()
            self.configure_stage(self.view_step.get())
            self.refresh_view()
            self.status_var.set(f"Aktivna etaža: {self.active_level.name}")

    def apply_orientation(self) -> None:
        try:
            azimuth = float(self.orientation_var.get()) % 360.0
            orientation = BuildingOrientation(north_azimuth_deg=azimuth)
            self.workflow.model.set_orientation(orientation)
            self.workflow.ensure_project_spec().set_orientation(azimuth)
        except ValueError as exc:
            messagebox.showwarning("LAT-CES", str(exc), parent=self)
            return
        self.refresh_view()

    def update_orientation_info(self) -> None:
        o = self.workflow.model.orientation
        self.orientation_info.configure(text=f"N {o.north_azimuth_deg:.1f}° · E {o.east_azimuth_deg:.1f}° · S {o.south_azimuth_deg:.1f}° · W {o.west_azimuth_deg:.1f}°")

    def apply_roof(self) -> None:
        try:
            roof = self.workflow.set_roof(self.roof_type_var.get().strip(), float(self.roof_height_var.get()), construction=self.roof_construction_var.get().strip(), covering=self.roof_covering_var.get().strip(), substructure=self.roof_substructure_var.get().strip(), support=self.roof_support_var.get().strip(), length_m=float(self.level_length_var.get()), width_m=float(self.level_width_var.get()), slope_deg=float(self.roof_slope_var.get()))
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Krov", str(exc), parent=self)
            return
        self.status_var.set(f"Krov primijenjen: {roof.roof_type}, nagib {roof.slope_deg:.1f}°")
        self.refresh_view()

    def apply_level_spec(self) -> None:
        try:
            name = self.level_name_var.get().strip()
            height, length, width = float(self.height_var.get()), float(self.level_length_var.get()), float(self.level_width_var.get())
            if not name or height <= 0 or length <= 0 or width <= 0:
                raise ValueError("Naziv i dimenzije etaže moraju biti pozitivni")
            level = self.active_level
            level.name, level.height, level.length_m, level.width_m = name, height, length, width
            if level.floor_plan is None or not level.floor_plan.walls:
                level.set_floor_plan(make_square_floor_plan(name, max(length, width)))
            level.floor_plan.name = name
        except ValueError as exc:
            messagebox.showwarning("LAT-CES — Etaža", str(exc), parent=self)
            return
        self.refresh_view()
        self.status_var.set(f"Etaža primijenjena: {name} · {length:.2f} × {width:.2f} × {height:.2f} m")

    def add_level(self) -> None:
        try:
            height, length, width = float(self.height_var.get() or 2.80), float(self.level_length_var.get() or 10.0), float(self.level_width_var.get() or 10.0)
            if height <= 0 or length <= 0 or width <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("LAT-CES", "Dimenzije etaže moraju biti pozitivne.", parent=self)
            return
        levels = list(self.workflow.model.levels.values())
        previous = levels[-1] if levels else None
        elevation = previous.top_elevation if previous else 0.0
        number = len(levels) + 1
        level = Level(name=f"Etaža {number}", elevation=elevation, height=height, length_m=length, width_m=width, floor_plan=make_square_floor_plan(f"Etaža {number}", max(length, width)))
        self.workflow.model.add_level(level)
        self.workflow.active_level_id = level.level_id
        self.view_step.set(2)
        self.configure_stage(2)
        self.refresh_view()
        self.status_var.set(f"Dodana {level.name}")

    def canvas_to_model(self, x: float, y: float) -> Point2D:
        width, height = max(self.canvas.winfo_width(), 400), max(self.canvas.winfo_height(), 300)
        xmin, xmax, ymin, ymax = self.plan_bounds()
        margin = 80
        scale = min((width - 2 * margin) / max(xmax - xmin, 1.0), (height - 2 * margin) / max(ymax - ymin, 1.0))
        origin_x = (width - (xmax - xmin) * scale) / 2 - xmin * scale
        origin_y = (height + (ymax - ymin) * scale) / 2 + ymin * scale
        return Point2D((x - origin_x) / scale, (origin_y - y) / scale)

    def model_to_canvas(self, point: Point2D) -> tuple[float, float]:
        width, height = max(self.canvas.winfo_width(), 400), max(self.canvas.winfo_height(), 300)
        xmin, xmax, ymin, ymax = self.plan_bounds()
        margin = 80
        scale = min((width - 2 * margin) / max(xmax - xmin, 1.0), (height - 2 * margin) / max(ymax - ymin, 1.0))
        origin_x = (width - (xmax - xmin) * scale) / 2 - xmin * scale
        origin_y = (height + (ymax - ymin) * scale) / 2 + ymin * scale
        return origin_x + point.x * scale, origin_y - point.y * scale

    def plan_bounds(self) -> tuple[float, float, float, float]:
        points = [p for wall in self.floor_plan.walls.values() for p in (wall.segment.start, wall.segment.end)]
        if not points:
            return 0.0, 10.0, 0.0, 10.0
        xs, ys = [p.x for p in points], [p.y for p in points]
        pad = 1.0
        return min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad

    def draw_compass(self) -> None:
        o = self.workflow.model.orientation
        width = max(self.canvas.winfo_width(), 400)
        cx, cy, radius = width - 70, 70, 32
        angle = math.radians(-o.north_azimuth_deg + 90.0)
        nx, ny = cx + radius * math.cos(angle), cy - radius * math.sin(angle)
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline="#6b7280", width=2)
        self.canvas.create_line(cx, cy, nx, ny, arrow=tk.LAST, width=3)
        self.canvas.create_text(cx, cy + radius + 12, text=f"N {o.north_azimuth_deg:.1f}°", fill="#374151")

    def draw_floor_plan(self) -> None:
        self.canvas.delete("all")
        width, height = max(self.canvas.winfo_width(), 400), max(self.canvas.winfo_height(), 300)
        xmin, xmax, ymin, ymax = self.plan_bounds()
        for x in range(math.floor(xmin), math.ceil(xmax) + 1):
            px, _ = self.model_to_canvas(Point2D(float(x), 0.0))
            self.canvas.create_line(px, 0, px, height, fill="#edf0f2")
        for y in range(math.floor(ymin), math.ceil(ymax) + 1):
            _, py = self.model_to_canvas(Point2D(0.0, float(y)))
            self.canvas.create_line(0, py, width, py, fill="#edf0f2")
        for wall in self.floor_plan.walls.values():
            x1, y1 = self.model_to_canvas(wall.segment.start)
            x2, y2 = self.model_to_canvas(wall.segment.end)
            selected = wall.wall_id == self.editor.selected_wall_id
            self.canvas.create_line(x1, y1, x2, y2, width=10 if selected else 7, fill="#2563eb" if selected else "#111827")
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10, text=f"{wall.segment.length:.2f} m", fill="#374151")
            for opening in wall.openings:
                t1, t2 = opening.offset / wall.segment.length, (opening.offset + opening.width) / wall.segment.length
                ox1, oy1 = x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1
                ox2, oy2 = x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2
                self.canvas.create_line(ox1, oy1, ox2, oy2, width=10, fill="white")
                self.canvas.create_text((ox1 + ox2) / 2, (oy1 + oy2) / 2 + 12, text=f"{opening.kind} {opening.width:.2f} m", fill="#4b5563", font=("Segoe UI", 8))
        self.draw_compass()
        self.canvas.create_text(20, height - 20, text=f"Etaža: {self.active_level.name}", anchor="sw", fill="#5f6368")

    def draw_section(self) -> None:
        self.canvas.delete("all")
        try:
            axis = SectionAxis(self.section_axis_var.get())
            position = float(self.section_position_var.get())
        except ValueError:
            self.status_var.set("Neispravan pravac ili položaj presjeka")
            return
        style = ViewStyle(self.view_style_var.get())
        geometries = build_geometry(self.workflow.model)
        section = SectionView(SectionDefinition(axis=axis, position_m=position, style=style), geometries)
        width, height = max(self.canvas.winfo_width(), 500), max(self.canvas.winfo_height(), 350)
        if not geometries:
            return
        total_h = sum(g.height for g in geometries) + (self.workflow.model.roof.height_m if self.workflow.model.roof else 0.0)
        scale = min((width - 120) / 10.0, (height - 100) / max(total_h, 3.0))
        base_y = height - 55
        for idx, geometry in enumerate(geometries):
            z0 = sum(g.height for g in geometries[:idx])
            for wall in geometry.walls:
                coord = wall.x1 if axis is SectionAxis.X else wall.y1
                if abs(coord - position) > max(wall.thickness, 0.25):
                    continue
                span = max(abs(wall.y2 - wall.y1) if axis is SectionAxis.X else abs(wall.x2 - wall.x1), 1.0)
                x0, x1 = 70, 70 + span * scale
                y0, y1 = base_y - z0 * scale, base_y - (z0 + wall.height) * scale
                if section.is_line_based:
                    self.canvas.create_rectangle(x0, y1, x1, y0, outline="#111827", width=2)
                else:
                    self.canvas.create_rectangle(x0, y1, x1, y0, fill="#d8c8ad", outline="#6b5b4b", width=2)
        title = "KONSTRUKCIJSKI LINIJSKI PRESJEK" if section.is_line_based else "PRIRODNI PRESJEK"
        self.canvas.create_text(20, 20, text=f"{title} · {axis.value} · {position:.2f} m", anchor="nw", fill="#111827", font=("Segoe UI", 12, "bold"))
        self.draw_compass()

    def project_3d(self, x: float, y: float, z: float, scale: float, width: float, height: float) -> tuple[float, float]:
        az = math.radians(self.workflow.model.orientation.north_azimuth_deg)
        xr = x * math.cos(az) - y * math.sin(az)
        yr = x * math.sin(az) + y * math.cos(az)
        return width * 0.28 + xr * scale + yr * 0.48 * scale, height * 0.76 - z * scale - yr * 0.24 * scale

    def draw_3d(self) -> None:
        self.canvas.delete("all")
        geometries = build_geometry(self.workflow.model)
        width, height = max(self.canvas.winfo_width(), 500), max(self.canvas.winfo_height(), 350)
        style = ViewStyle(self.view_style_var.get())
        scale = 24.0
        for idx, geometry in enumerate(geometries):
            z0 = sum(g.height for g in geometries[:idx])
            for wall in geometry.walls:
                a0 = self.project_3d(wall.x1, wall.y1, z0, scale, width, height)
                b0 = self.project_3d(wall.x2, wall.y2, z0, scale, width, height)
                a1 = self.project_3d(wall.x1, wall.y1, z0 + wall.height, scale, width, height)
                b1 = self.project_3d(wall.x2, wall.y2, z0 + wall.height, scale, width, height)
                if style is ViewStyle.CONSTRUCTIONAL_LINE:
                    for p, q in ((a0, b0), (a1, b1), (a0, a1), (b0, b1)):
                        self.canvas.create_line(*p, *q, fill="#374151", width=2)
                else:
                    self.canvas.create_polygon(*a0, *b0, *b1, *a1, fill="#d8c8ad", outline="#6b5b4b")
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
        self.canvas.create_text(20, 20, text=f"{title} · jedinstveni BuildingModel", anchor="nw", fill="#374151", font=("Segoe UI", 12, "bold"))
        self.draw_compass()

    def redraw_active_view(self) -> None:
        step = self.view_step.get()
        if step == 3:
            self.draw_floor_plan()
        elif step == 4:
            self.draw_section()
        elif step == 5:
            self.draw_3d()
        else:
            self.canvas.delete("all")
            self.canvas.create_text(30, 30, text=f"{dict(STEPS)[step]} — Building Model", anchor="nw", font=("Segoe UI", 18, "bold"), fill="#1f2937")
            self.draw_compass()

    def refresh_view(self) -> None:
        self.refresh_level_combo()
        self.update_selected_wall()
        self.update_orientation_info()
        self.update_summary()
        self.redraw_active_view()

    def update_selected_wall(self) -> None:
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        self.selected_length_var.set(f"{wall.segment.length:.2f}" if wall else "—")
        self.selected_thickness_var.set(f"{wall.thickness:.2f}" if wall else "0.20")

    def apply_wall_dimensions(self) -> None:
        wall = self.floor_plan.walls.get(self.editor.selected_wall_id) if self.editor.selected_wall_id else None
        if wall is None:
            messagebox.showinfo("LAT-CES", "Prvo odaberi zid.", parent=self)
            return
        try:
            new_length, thickness = float(self.selected_length_var.get()), float(self.selected_thickness_var.get())
            if new_length <= 0 or thickness <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("LAT-CES", "Dimenzije moraju biti pozitivne.", parent=self)
            return
        dx, dy = wall.segment.end.x - wall.segment.start.x, wall.segment.end.y - wall.segment.start.y
        old_length = wall.segment.length
        wall.thickness = thickness
        if old_length > 0:
            ux, uy = dx / old_length, dy / old_length
            wall.segment = Segment2D(wall.segment.start, Point2D(wall.segment.start.x + ux * new_length, wall.segment.start.y + uy * new_length))
        self.refresh_view()

    def validate_model(self) -> None:
        findings = self.workflow.validate()
        if findings:
            messagebox.showwarning("LAT-CES — Provjera", "\n".join(findings), parent=self)
            self.status_var.set(f"Model nije validan: {len(findings)} nalaza")
        else:
            messagebox.showinfo("LAT-CES — Provjera", "Building Model je validan.", parent=self)
            self.status_var.set("Building Model je validan")

    def update_summary(self) -> None:
        model = self.workflow.model
        roof = model.roof
        text = [f"Objekat: {model.name}", f"Etaže: {len(model.levels)}", f"Aktivna: {self.active_level.name}", f"Površina: {model.floor_area:.2f} m²", f"Zapremina: {model.volume:.2f} m³", f"Sjever: {model.orientation.north_azimuth_deg:.1f}°", f"Pogled: {dict(STEPS)[self.view_step.get()]}", f"Stil: {self.view_style_var.get()}"]
        if roof:
            text.extend((f"Krov: {roof.roof_type}", f"Nagib: {roof.slope_deg:.1f}°", f"Visina krova: {roof.height_m:.2f} m"))
        text.extend(("", *[f"{i + 1}. {level.name}: {level.height:.2f} m" for i, level in enumerate(model.levels.values())]))
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", "\n".join(text))
        self.summary_text.configure(state="disabled")

    def save_project(self) -> None:
        self.workflow.current_step = self.view_step.get()
        target = self.model_path.get() or filedialog.asksaveasfilename(title="Sačuvaj Building Model", defaultextension=".json", filetypes=(("LAT-CES Building JSON", "*.json"), ("All files", "*.*")), initialfile="building_model.json")
        if not target:
            return
        try:
            save_workflow(self.workflow, target)
            self.model_path.set(target)
            self.status_var.set(f"Konfiguracija sačuvana: {target}")
        except Exception as exc:
            messagebox.showerror("LAT-CES", str(exc), parent=self)

    def load_project(self) -> None:
        target = filedialog.askopenfilename(title="Učitaj Building Model", filetypes=(("LAT-CES Building JSON", "*.json"), ("All files", "*.*")))
        if not target:
            return
        try:
            self.workflow = load_workflow(target)
            self.editor = FloorPlanEditor(self)
            self.model_path.set(target)
            self.view_step.set(min(max(self.workflow.current_step, 1), 5))
            self.refresh_level_combo()
            self.configure_stage(self.view_step.get())
            self.refresh_view()
            self.status_var.set(f"Konfiguracija učitana: {target}")
        except Exception as exc:
            messagebox.showerror("LAT-CES", str(exc), parent=self)

    def new_project(self) -> None:
        self.workflow = self.new_workflow()
        self.editor = FloorPlanEditor(self)
        self.model_path.set("")
        self.view_step.set(1)
        self.apply_default_orientation()
        self.configure_stage(1)
        self.refresh_view()
        self.status_var.set("Novi projekat")

    def open_analysis(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("LAT-CES — Scientific Analysis")
        dialog.geometry("860x620")
        dialog.transient(self)
        cfg = ttk.Frame(dialog, padding=14)
        cfg.pack(fill="x")
        path_var, output_var = tk.StringVar(), tk.StringVar()
        ttk.Label(cfg, text="JSON konfiguracija:").grid(row=0, column=0, sticky="w")
        ttk.Entry(cfg, textvariable=path_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(cfg, text="Browse…", command=lambda: path_var.set(filedialog.askopenfilename(filetypes=(("JSON files", "*.json"), ("All files", "*.*"))))).grid(row=0, column=2)
        ttk.Label(cfg, text="Output:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(cfg, textvariable=output_var).grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=(8, 0))
        cfg.columnconfigure(1, weight=1)
        result = tk.Text(dialog, wrap="word", font=("Consolas", 10))
        result.pack(fill="both", expand=True, padx=14, pady=8)

        def run() -> None:
            config_file = Path(path_var.get().strip())
            if not config_file.exists():
                messagebox.showwarning("LAT-CES", "Odaberi validnu JSON konfiguraciju.", parent=dialog)
                return
            try:
                config = load_config(config_file)
                report, exporter = analyze_config(config, project_default="LAT-CES Desktop Analysis", plenum_default="PLENUM-GUI-01", equation_default="Custom equation")
                output = Path(output_var.get().strip() or config_file.with_name("latces_report.json"))
                export_report(exporter, output, "json")
                content = json.loads(exporter.to_json())
                result.delete("1.0", "end")
                result.insert("1.0", f"Status: [{report.status.value}]\nReport: {output}\n\n{json.dumps(content, indent=2, ensure_ascii=False)}")
            except Exception as exc:
                result.delete("1.0", "end")
                result.insert("1.0", f"Analysis failed:\n\n{exc}")

        ttk.Button(dialog, text="Run Analysis", command=run).pack(pady=(0, 14))


def main() -> None:
    LATCESApp().mainloop()


if __name__ == "__main__":
    main()
