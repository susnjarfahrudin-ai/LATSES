from pathlib import Path
import re


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path}: {count}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def regex_once(path: Path, pattern: str, repl: str) -> None:
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(pattern, repl, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise SystemExit(f"Expected exactly one regex match in {path}: {count}")
    path.write_text(new_text, encoding="utf-8")


gui = Path("lat_ces/gui_enhanced.py")
replace_once(
    gui,
    "        self.drag_payload: str | None = None\n",
    "        self.drag_payload: str | None = None\n        self.selected_room_id: str | None = None\n        self.room_drag_last: Point2D | None = None\n",
)
replace_once(
    gui,
    '        self.canvas.bind("<Button-5>", self._zoom_out_linux, add="+")\n',
    '        self.canvas.bind("<Button-5>", self._zoom_out_linux, add="+")\n        self.canvas.bind("<ButtonPress-1>", self._room_press, add="+")\n        self.canvas.bind("<B1-Motion>", self._room_drag, add="+")\n        self.canvas.bind("<ButtonRelease-1>", self._room_release, add="+")\n',
)
replace_once(
    gui,
    '        self.canvas.bind("<ButtonRelease-1>", self._drop_payload, add="+")\n',
    '        selected_room = ttk.LabelFrame(side, text="Odabrana prostorija", padding=8)\n        selected_room.pack(fill="x", pady=(10, 0))\n        self.selected_room_name_var = tk.StringVar(value="—")\n        self.selected_room_length_var = tk.StringVar(value="—")\n        self.selected_room_width_var = tk.StringVar(value="—")\n        self._field(selected_room, "Naziv", self.selected_room_name_var, 0)\n        self._field(selected_room, "Dužina (m)", self.selected_room_length_var, 1)\n        self._field(selected_room, "Širina (m)", self.selected_room_width_var, 2)\n        ttk.Button(selected_room, text="Primijeni dimenzije prostorije", command=self.apply_selected_room_dimensions).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))\n        ttk.Label(selected_room, text="Alat Pomjeri premješta odabranu prostoriju.", wraplength=315).grid(row=4, column=0, columnspan=2, sticky="w", pady=(5, 0))\n\n        self.canvas.bind("<ButtonRelease-1>", self._drop_payload, add="+")\n',
)
replace_once(
    gui,
    '        level.add_room(room)\n        self.status_var.set(f"Dodana prostorija: {name} · {length:.2f} × {width:.2f} m")\n        self.refresh_view()\n\n',
    '        level.add_room(room)\n        self.selected_room_id = room.room_id\n        self._update_selected_room_fields()\n        self.status_var.set(f"Dodana prostorija: {name} · {length:.2f} × {width:.2f} m")\n        self.refresh_view()\n\n',
)
regex_once(
    gui,
    r'(?ms)^    def _drop_partition\(self, point: Point2D\) -> None:\n',
    '''    def _room_at(self, point: Point2D):\n        for room in reversed(tuple(self.active_level.rooms.values())):\n            fp = room.footprint\n            if fp.origin.x <= point.x <= fp.max_point.x and fp.origin.y <= point.y <= fp.max_point.y:\n                return room\n        return None\n\n    def _room_press(self, event: tk.Event) -> None:\n        if self.view_step.get() != 3 or self.editor.tool not in {"select", "move"}:\n            return\n        point = self.snap_point(self.canvas_to_model(event.x, event.y))\n        room = self._room_at(point)\n        if room is None:\n            return\n        self.selected_room_id = room.room_id\n        self._update_selected_room_fields()\n        if self.editor.tool == "move":\n            self.room_drag_last = point\n            self.status_var.set(f"Odabrana prostorija: {room.name} — povuci je na novu poziciju")\n        else:\n            self.room_drag_last = None\n            self.status_var.set(f"Odabrana prostorija: {room.name} · {room.footprint.length:.2f} × {room.footprint.width:.2f} m")\n        self.refresh_view()\n\n    def _room_drag(self, event: tk.Event) -> None:\n        if self.view_step.get() != 3 or self.editor.tool != "move" or not self.selected_room_id or self.room_drag_last is None:\n            return\n        room = self.active_level.rooms.get(self.selected_room_id)\n        if room is None:\n            self.room_drag_last = None\n            return\n        point = self.snap_point(self.canvas_to_model(event.x, event.y))\n        dx, dy = point.x - self.room_drag_last.x, point.y - self.room_drag_last.y\n        fp = room.footprint\n        max_x = max(0.0, (self.active_level.length_m or self.plan_bounds()[1]) - fp.length)\n        max_y = max(0.0, (self.active_level.width_m or self.plan_bounds()[3]) - fp.width)\n        new_x = min(max(fp.origin.x + dx, 0.0), max_x)\n        new_y = min(max(fp.origin.y + dy, 0.0), max_y)\n        room.footprint = Box3D(Point3D(new_x, new_y, fp.origin.z), fp.length, fp.width, fp.height)\n        self.room_drag_last = point\n        self._update_selected_room_fields()\n        self.refresh_view()\n\n    def _room_release(self, _event: tk.Event) -> None:\n        if self.room_drag_last is not None:\n            self.status_var.set("Položaj prostorije ažuriran u BuildingModelu")\n        self.room_drag_last = None\n\n    def _update_selected_room_fields(self) -> None:\n        if not hasattr(self, "selected_room_name_var"):\n            return\n        room = self.active_level.rooms.get(self.selected_room_id) if self.selected_room_id else None\n        if room is None:\n            self.selected_room_name_var.set("—")\n            self.selected_room_length_var.set("—")\n            self.selected_room_width_var.set("—")\n            return\n        self.selected_room_name_var.set(room.name)\n        self.selected_room_length_var.set(f"{room.footprint.length:.2f}")\n        self.selected_room_width_var.set(f"{room.footprint.width:.2f}")\n\n    def apply_selected_room_dimensions(self) -> None:\n        room = self.active_level.rooms.get(self.selected_room_id) if self.selected_room_id else None\n        if room is None:\n            messagebox.showinfo("LAT-CES — Prostorija", "Prvo odaberi prostoriju na tlocrtu.", parent=self)\n            return\n        try:\n            length = float(self.selected_room_length_var.get())\n            width = float(self.selected_room_width_var.get())\n            if length <= 0 or width <= 0:\n                raise ValueError("Dimenzije prostorije moraju biti > 0")\n        except ValueError as exc:\n            messagebox.showwarning("LAT-CES — Prostorija", str(exc), parent=self)\n            return\n        level_length = self.active_level.length_m or self.plan_bounds()[1]\n        level_width = self.active_level.width_m or self.plan_bounds()[3]\n        if length > level_length or width > level_width:\n            messagebox.showwarning("LAT-CES — Prostorija", "Dimenzije prostorije moraju stati u aktivnu etažu.", parent=self)\n            return\n        max_x = max(0.0, level_length - length)\n        max_y = max(0.0, level_width - width)\n        origin = room.footprint.origin\n        x, y = min(max(origin.x, 0.0), max_x), min(max(origin.y, 0.0), max_y)\n        room.footprint = Box3D(Point3D(x, y, origin.z), length, width, room.footprint.height)\n        self._update_selected_room_fields()\n        self.status_var.set(f"Prostorija dimenzionirana: {length:.2f} × {width:.2f} m")\n        self.refresh_view()\n\n    def _drop_partition(self, point: Point2D) -> None:\n''',
)
regex_once(
    gui,
    r'(?ms)^        for room in self\.active_level\.rooms\.values\(\):\n            fp = room\.footprint\n            x1, y1 = self\.model_to_canvas\(Point2D\(fp\.origin\.x, fp\.origin\.y\)\)\n            x2, y2 = self\.model_to_canvas\(Point2D\(fp\.max_point\.x, fp\.max_point\.y\)\)\n            self\.canvas\.create_rectangle\(x1, y1, x2, y2, outline="#0f766e", dash=\(5, 3\), width=2\)\n            cx, cy = \(x1 \+ x2\) / 2\.0, \(y1 \+ y2\) / 2\.0\n            self\.canvas\.create_text\(cx, cy, text=f"\{room\.name\}\\n\{room\.footprint\.length:\.2f\} × \{room\.footprint\.width:\.2f\} m", fill="#0f766e", font=\("Segoe UI", 9, "bold"\)\)\n',
    '''        for room in self.active_level.rooms.values():\n            fp = room.footprint\n            x1, y1 = self.model_to_canvas(Point2D(fp.origin.x, fp.origin.y))\n            x2, y2 = self.model_to_canvas(Point2D(fp.max_point.x, fp.max_point.y))\n            selected = room.room_id == self.selected_room_id\n            self.canvas.create_rectangle(x1, y1, x2, y2, outline="#0369a1" if selected else "#0f766e", dash=(5, 3), width=3 if selected else 2)\n            if selected:\n                for hx, hy in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):\n                    self.canvas.create_rectangle(hx - 4, hy - 4, hx + 4, hy + 4, fill="#0369a1", outline="")\n            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0\n            self.canvas.create_text(cx, cy, text=f"{room.name}\\n{room.footprint.length:.2f} × {room.footprint.width:.2f} m", fill="#0369a1" if selected else "#0f766e", font=("Segoe UI", 9, "bold"))\n''',
)

complete = Path("lat_ces/gui_complete.py")
regex_once(
    complete,
    r'(?ms)^        draft = ttk\.Frame\(quick\)\n        draft\.pack\(fill="x", pady=\(6, 0\)\)\n        for text, command in \(\(.*?\)\):\n            ttk\.Button\(draft, text=text, command=command\)\.pack\(side="left", expand=True, fill="x", padx=2\)\n',
    '''        draft = ttk.Frame(quick)\n        draft.pack(fill="x", pady=(6, 0))\n        for text, command in (("Tlocrt", lambda: self._set_view_step(3)), ("Zid", self._open_wall_editor), ("Prostorija", lambda: self._start_payload("room"))):\n            ttk.Button(draft, text=text, command=command).pack(side="left", expand=True, fill="x", padx=2)\n        openings = ttk.Frame(quick)\n        openings.pack(fill="x", pady=(4, 0))\n        for text, command in (("Vrata", lambda: self._start_payload("door")), ("Prozor", lambda: self._start_payload("window"))):\n            ttk.Button(openings, text=text, command=command).pack(side="left", expand=True, fill="x", padx=2)\n''',
)

print("Reference House room/window UI patch applied")
