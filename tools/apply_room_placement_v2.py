from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}: {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


gui = Path("lat_ces/gui_enhanced.py")
replace_once(gui,
    '        self.selected_room_id: str | None = None\n        self.room_drag_last: Point2D | None = None\n',
    '        self.selected_room_id: str | None = None\n        self.room_drag_last: Point2D | None = None\n        self.room_placing = False\n')
replace_once(gui,
    '        self._field(room_box, "Dužina (m)", self.room_length_var, 1)\n        self._field(room_box, "Širina (m)", self.room_width_var, 2)\n        self._drag_label(room_box, "▣  PROSTORIJA  — povuci", "room")\n\n        partition_box = ttk.LabelFrame(palette, text="Pregradni zid", padding=6)\n        partition_box.pack(fill="x", pady=6)\n        self.partition_length_var = tk.StringVar(value="3.00")\n        self.partition_thickness_var = tk.StringVar(value="0.12")\n        self._field(partition_box, "Dužina (m)", self.partition_length_var, 0)\n        self._field(partition_box, "Debljina (m)", self.partition_thickness_var, 1)\n        self._drag_label(partition_box, "━  PREGRADNI ZID  — povuci", "partition")\n',
    '        self._field(room_box, "Dužina (m)", self.room_length_var, 1)\n        self._field(room_box, "Širina (m)", self.room_width_var, 2)\n        ttk.Button(room_box, text="＋ Nova prostorija — postavi na tlocrt", command=self._start_room_placement).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))\n        self._drag_label(room_box, "▣  PROSTORIJA  — povuci", "room")\n\n')
replace_once(gui,
    '    def _start_payload(self, payload: str) -> None:\n',
    '    def _start_room_placement(self) -> None:\n        if self.view_step.get() != 3:\n            self.view_step.set(3)\n            self.goto_step()\n        self.editor.set_tool("select")\n        self.drag_payload = None\n        self.room_placing = True\n        self.status_var.set("Nova prostorija: provjeri dužinu i širinu, zatim klikni mjesto unutar kuće.")\n\n    def _start_payload(self, payload: str) -> None:\n')
replace_once(gui,
    '    def _room_press(self, event: tk.Event) -> None:\n        if self.view_step.get() != 3 or self.editor.tool not in {"select", "move"}:\n            return\n        point = self.snap_point(self.canvas_to_model(event.x, event.y))\n',
    '    def _room_press(self, event: tk.Event) -> None:\n        if self.view_step.get() != 3:\n            return\n        point = self.snap_point(self.canvas_to_model(event.x, event.y))\n        if self.room_placing:\n            self._drop_room(point)\n            self.room_placing = False\n            self.status_var.set("Prostorija postavljena. Možeš je odmah odabrati i urediti.")\n            return\n        if self.editor.tool not in {"select", "move"}:\n            return\n')
replace_once(gui,
    '        level.add_room(room)\n        self.selected_room_id = room.room_id\n',
    '        level.add_room(room)\n        self._sync_room_partition_walls(room)\n        self.selected_room_id = room.room_id\n')
replace_once(gui,
    '        room.footprint = Box3D(Point3D(new_x, new_y, fp.origin.z), fp.length, fp.width, fp.height)\n        self.room_drag_last = point\n',
    '        room.footprint = Box3D(Point3D(new_x, new_y, fp.origin.z), fp.length, fp.width, fp.height)\n        self._sync_room_partition_walls(room)\n        self.room_drag_last = point\n')
replace_once(gui,
    '        room.footprint = Box3D(Point3D(x, y, origin.z), length, width, room.footprint.height)\n        self._update_selected_room_fields()\n',
    '        room.footprint = Box3D(Point3D(x, y, origin.z), length, width, room.footprint.height)\n        self._sync_room_partition_walls(room)\n        self._update_selected_room_fields()\n')
replace_once(gui,
    '    def _drop_partition(self, point: Point2D) -> None:\n',
    '    def _sync_room_partition_walls(self, room: Room) -> None:\n        """Derive interior wall segments from the room rectangle."""\n        fp = room.footprint\n        level = self.active_level\n        xmin, xmax = fp.origin.x, fp.origin.x + fp.length\n        ymin, ymax = fp.origin.y, fp.origin.y + fp.width\n        edges = ((Point2D(xmin, ymin), Point2D(xmax, ymin)), (Point2D(xmax, ymin), Point2D(xmax, ymax)), (Point2D(xmax, ymax), Point2D(xmin, ymax)), (Point2D(xmin, ymax), Point2D(xmin, ymin)))\n        tol = 0.001\n        def exterior(a: Point2D, b: Point2D) -> bool:\n            return ((abs(a.x) < tol and abs(b.x) < tol) or (abs(a.y) < tol and abs(b.y) < tol) or (abs(a.x - level.length_m) < tol and abs(b.x - level.length_m) < tol) or (abs(a.y - level.width_m) < tol and abs(b.y - level.width_m) < tol))\n        for index, (a, b) in enumerate(edges, 1):\n            if exterior(a, b):\n                continue\n            name = f"Zid prostorije {room.room_id} {index}"\n            existing = next((w for w in self.floor_plan.walls.values() if w.name == name), None)\n            if existing is not None:\n                existing.segment = Segment2D(a, b)\n                continue\n            shared = next((w for w in self.floor_plan.walls.values() if w.name.startswith("Zid prostorije ") and ((abs(w.segment.start.x-a.x)<tol and abs(w.segment.start.y-a.y)<tol and abs(w.segment.end.x-b.x)<tol and abs(w.segment.end.y-b.y)<tol) or (abs(w.segment.start.x-b.x)<tol and abs(w.segment.start.y-b.y)<tol and abs(w.segment.end.x-a.x)<tol and abs(w.segment.end.y-a.y)<tol))), None)\n            if shared is None:\n                self.floor_plan.add_wall(Wall(name=name, segment=Segment2D(a, b), thickness=0.12))\n\n    def _drop_partition(self, point: Point2D) -> None:\n')

gui_core = Path("lat_ces/gui.py")
replace_once(gui_core,
    '            if math.hypot(point.x - self.start_point.x, point.y - self.start_point.y) < 0.1:\n                return\n            wall = Wall(name=f"Zid {self.floor_plan.wall_count + 1}", segment=Segment2D(self.start_point, point), thickness=0.20)\n',
    '            dx = point.x - self.start_point.x\n            dy = point.y - self.start_point.y\n            if math.hypot(dx, dy) < 0.1:\n                return\n            reference = self.nearest_wall(self.start_point, tolerance_m=2.0)\n            if reference is not None and reference.segment.length > 0:\n                angle = math.atan2(reference.segment.end.y - reference.segment.start.y, reference.segment.end.x - reference.segment.start.x)\n                candidate_angles = (angle, angle + math.pi / 2.0)\n                best = max(candidate_angles, key=lambda a: abs(dx * math.cos(a) + dy * math.sin(a)))\n                distance = math.hypot(dx, dy)\n                point = Point2D(self.start_point.x + distance * math.cos(best), self.start_point.y + distance * math.sin(best))\n            elif abs(dx) >= abs(dy):\n                point = Point2D(point.x, self.start_point.y)\n            else:\n                point = Point2D(self.start_point.x, point.y)\n            wall = Wall(name=f"Zid {self.floor_plan.wall_count + 1}", segment=Segment2D(self.start_point, point), thickness=0.20)\n')
print("Room placement v2 patch applied")
