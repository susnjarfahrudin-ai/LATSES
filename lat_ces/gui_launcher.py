"""Production desktop launcher with visible canonical BuildingModel engineering views."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from lat_ces.building.floor_plan import Point2D
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp as _CanonicalCompleteBuildingWorkspaceApp


class ProductionCompleteBuildingWorkspaceApp(_CanonicalCompleteBuildingWorkspaceApp):
    """Compatibility/presentation launcher layered on the canonical GUI.

    This subclass may add production-only presentation behavior, but it never
    mutates the canonical CompleteBuildingWorkspaceApp class at import time.
    """

    def __init__(self) -> None:
        super().__init__()
        self._apply_natural_blue_atmosphere()

    def _apply_natural_blue_atmosphere(self) -> None:
        """Give the engineering workspace the agreed calm sky/natural visual layer."""
        style = ttk.Style(self)
        try:
            style.configure("Natural.TFrame", background="#eaf4fb")
            style.configure("Natural.TLabel", background="#eaf4fb", foreground="#17324d")
            style.configure("Natural.TLabelframe", background="#eaf4fb", foreground="#17324d")
            style.configure("Natural.TLabelframe.Label", background="#eaf4fb", foreground="#17324d")
            style.configure("Natural.TNotebook", background="#dbeef9", borderwidth=0)
            style.configure("Natural.TNotebook.Tab", background="#cfe7f5", foreground="#17324d", padding=(12, 6))
            style.map("Natural.TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#0f3d5e")])
            style.configure("Natural.TButton", padding=(9, 5))
        except tk.TclError:
            pass
        self.configure(background="#eaf4fb")
        self.option_add("*Font", ("Segoe UI", 9))
        if hasattr(self, "canvas"):
            self.canvas.configure(background="#f6fbfe", highlightbackground="#a9c9dc")
        for child in self.winfo_children():
            if isinstance(child, ttk.Frame):
                try:
                    child.configure(style="Natural.TFrame")
                except tk.TclError:
                    pass

    def _build_model_tab(self, tab: ttk.Frame) -> None:
        super()._build_model_tab(tab)
        ttk.Button(tab, text="Model Inspector", command=self.show_canonical_model_inspector).pack(side="left", padx=(10, 2))

    def _draw_sky_and_umbrella(self) -> None:
        """Render the visible sky and umbrella decoration behind the engineering view."""
        canvas = getattr(self, "canvas", None)
        if canvas is None:
            return
        width = max(canvas.winfo_width(), 700)
        height = max(canvas.winfo_height(), 450)
        canvas.create_rectangle(0, 0, width, height, fill="#dff3ff", outline="", tags="natural-atmosphere")
        for x, y, r in ((110, 70, 34), (220, 105, 24), (330, 62, 30), (500, 92, 27)):
            canvas.create_oval(x-r, y-r, x+r, y+r, fill="#ffffff", outline="", tags="natural-atmosphere")
        cx, cy = width - 105, 92
        canvas.create_arc(cx-58, cy-30, cx+58, cy+42, start=0, extent=180, fill="#f5b84b", outline="#7a4b00", width=2, tags="natural-atmosphere")
        canvas.create_line(cx, cy+6, cx, cy+82, fill="#4b5563", width=3, tags="natural-atmosphere")
        canvas.create_arc(cx-10, cy+72, cx+12, cy+95, start=270, extent=180, style="arc", outline="#4b5563", width=3, tags="natural-atmosphere")

    def _draw_canonical_elements(self) -> None:
        level = self.active_level
        for room in level.rooms.values():
            fp = room.footprint
            p1 = self.model_to_canvas(Point2D(fp.origin.x, fp.origin.y)); p3 = self.model_to_canvas(Point2D(fp.origin.x + fp.length, fp.origin.y + fp.width))
            self.canvas.create_rectangle(min(p1[0], p3[0]), min(p1[1], p3[1]), max(p1[0], p3[0]), max(p1[1], p3[1]), outline="#64748b", width=1)
            self.canvas.create_text((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2, text=room.name, fill="#374151", font=("Segoe UI", 9, "bold"))
        for stair in level.stairs.values():
            fp = stair.footprint
            p1 = self.model_to_canvas(Point2D(fp.origin.x, fp.origin.y)); p3 = self.model_to_canvas(Point2D(fp.origin.x + fp.length, fp.origin.y + fp.width))
            self.canvas.create_rectangle(min(p1[0], p3[0]), min(p1[1], p3[1]), max(p1[0], p3[0]), max(p1[1], p3[1]), outline="#2563eb", fill="#dbeafe", width=2, stipple="gray25")
            self.canvas.create_text((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2, text=f"Stepenište ({stair.riser_count or '?'})", fill="#1d4ed8")
        for terrace in level.terraces.values():
            fp = terrace.footprint
            p1 = self.model_to_canvas(Point2D(fp.origin.x, fp.origin.y)); p3 = self.model_to_canvas(Point2D(fp.origin.x + fp.length, fp.origin.y + fp.width))
            self.canvas.create_rectangle(min(p1[0], p3[0]), min(p1[1], p3[1]), max(p1[0], p3[0]), max(p1[1], p3[1]), outline="#b45309", fill="#fef3c7", width=2, stipple="gray25")
            self.canvas.create_text((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2, text="Terasa", fill="#92400e")

    def draw_floor_plan(self) -> None:
        super().draw_floor_plan()
        self._draw_sky_and_umbrella()
        self._draw_canonical_elements()


# Compatibility export for callers that historically imported the launcher name.
CompleteBuildingWorkspaceApp = ProductionCompleteBuildingWorkspaceApp


def run_gui_acceptance() -> None:
    """Run the deterministic visual acceptance path inside the packaged EXE."""
    app = CompleteBuildingWorkspaceApp()
    try:
        assert app.workflow.model.levels, "Canonical BuildingModel: no levels"
        for step, label in ((3, "Tlocrt"), (4, "Presjek"), (5, "3D")):
            app.view_step.set(step)
            app.goto_step()
            app.update_idletasks()
            if not app.canvas.find_all():
                raise RuntimeError(f"{label}: canvas has no rendered content")
        findings = app.workflow.validate()
        if findings:
            raise RuntimeError("Provjera: " + "; ".join(findings))
        app.refresh_engineering_summary()
        summary = app.engineering_summary.get("1.0", "end").strip()
        for marker in ("STATIKA", "TERMIKA", "KOLIČINE", "MEP"):
            if marker not in summary:
                raise RuntimeError(f"Izvještaj: missing {marker}")
        if not app.workflow.model.levels:
            raise RuntimeError("Canonical BuildingModel: no levels")
        print("GUI ACCEPTANCE GREEN: Canonical BuildingModel -> Tlocrt -> Presjek -> 3D -> Provjera -> Izvještaj")
    finally:
        app.destroy()


def main() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") == "1":
        run_gui_acceptance()
        return
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
