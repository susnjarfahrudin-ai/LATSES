"""Production desktop launcher with visible canonical BuildingModel engineering views."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from lat_ces.building.floor_plan import Point2D
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.structural import calculate_structural_loads
from lat_ces.building_model.quantities import to_quantity_view
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.thermal.building_model_adapter import to_thermal_input


_original_init = CompleteBuildingWorkspaceApp.__init__
_original_build_model_tab = CompleteBuildingWorkspaceApp._build_model_tab
_original_draw_floor_plan = CompleteBuildingWorkspaceApp.draw_floor_plan


def _build_model_tab_with_inspector(self: CompleteBuildingWorkspaceApp, tab: ttk.Frame) -> None:
    _original_build_model_tab(self, tab)
    ttk.Button(tab, text="Model Inspector", command=self.show_canonical_model_inspector).pack(side="left", padx=(10, 2))


def _add_record(tree: ttk.Treeview, kind: str, object_id: str, details: str) -> None:
    tree.insert("", "end", values=(kind, object_id, details))


def show_canonical_model_inspector(self: CompleteBuildingWorkspaceApp) -> None:
    window = tk.Toplevel(self)
    window.title("LAT-CES — Canonical Building Model")
    window.geometry("1050x620")
    window.transient(self)
    ttk.Label(window, text="Canonical BuildingModel — jedan fizički model / mnogo stručnih pogleda", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(10, 6))
    tree = ttk.Treeview(window, columns=("kind", "id", "details"), show="headings")
    tree.heading("kind", text="Objekat"); tree.heading("id", text="ID"); tree.heading("details", text="Podaci")
    tree.column("kind", width=130, anchor="w"); tree.column("id", width=330, anchor="w"); tree.column("details", width=550, anchor="w")
    tree.pack(fill="both", expand=True, padx=12, pady=6)
    model = self.workflow.model
    for level in model.levels.values():
        _add_record(tree, "Level", level.level_id, f"{level.name} · {level.length_m:.2f} × {level.width_m:.2f} m · h={level.height:.2f} m")
        for room in level.rooms.values():
            _add_record(tree, "Room", room.room_id, f"{room.name} · {room.floor_area:.2f} m² · V={room.volume:.2f} m³ · h={room.footprint.height:.2f} m")
        for stair in level.stairs.values():
            _add_record(tree, "Stair", stair.id, f"{stair.name} · {stair.length_m:.2f} × {stair.width_m:.2f} m · {stair.riser_count or 'N/A'} stepenika · h={stair.riser_height_m or 'N/A'} m · gazište={stair.tread_width_m or 'N/A'} m · podest={'DA' if stair.landing else 'NE'} · ograda={'DA' if stair.railing else 'NE'} · otvor={'DA' if stair.floor_opening else 'NE'}")
        for terrace in level.terraces.values():
            _add_record(tree, "Terrace", terrace.id, f"{terrace.name} · {terrace.length_m:.2f} × {terrace.width_m:.2f} m · {terrace.construction_type}")
        if level.floor_plan:
            for wall in level.floor_plan.walls.values():
                product = model.materials.get(wall.material_id) if wall.material_id else None
                _add_record(tree, "Wall", wall.wall_id, f"{wall.name} · {'vanjski' if wall.exterior else 'unutrašnji'} · {'nosivi' if wall.load_bearing else 'pregradni'} · Product={(product.resolved_product_id if product else 'N/A')}")
                for opening in wall.openings:
                    _add_record(tree, "Opening", opening.opening_id, f"{opening.kind} · {opening.width:.2f} × {opening.height_m:.2f} m · wall={wall.wall_id}")
    for material in model.materials.values():
        _add_record(tree, "Material/Product", material.material_id, f"{material.name} · Product={material.resolved_product_id} · λ={material.thermal_conductivity if material.thermal_conductivity is not None else 'N/A'} · ρ={material.density if material.density is not None else 'N/A'} · proizvođač={getattr(material, 'manufacturer', None) or 'N/A'}")


def _draw_canonical_elements(self: CompleteBuildingWorkspaceApp) -> None:
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


def _draw_floor_plan_with_elements(self: CompleteBuildingWorkspaceApp) -> None:
    _original_draw_floor_plan(self)
    _draw_canonical_elements(self)


def _install_engineering_summary(self: CompleteBuildingWorkspaceApp) -> None:
    if not hasattr(self, "complete_tabs"):
        return
    frame = ttk.Frame(self.complete_tabs, padding=10)
    self.complete_tabs.add(frame, text="Engineering Summary")
    ttk.Button(frame, text="Osvježi sve", command=self.refresh_engineering_summary).pack(anchor="w")
    self.engineering_summary = tk.Text(frame, height=22, wrap="word")
    self.engineering_summary.pack(fill="both", expand=True, pady=(8, 0)); self.engineering_summary.configure(state="disabled")
    self.refresh_engineering_summary()


def refresh_engineering_summary(self: CompleteBuildingWorkspaceApp) -> None:
    widget = getattr(self, "engineering_summary", None)
    if widget is None or not getattr(self, "workflow", None):
        return
    model = self.workflow.model
    q = to_quantity_view(model)
    registry = ensure_mep_registry(model)
    lines = ["CANONICAL BUILDING MODEL — ENGINEERING SUMMARY", ""]
    lines += ["STATIKA"]
    try:
        structural = calculate_structural_loads(model)
        lines += [f"Status: {structural.status}", f"Vertikalno linijsko opterećenje: {structural.total_vertical_line_load_kn_m:.3f} kN/m", f"Zidovi: {len(structural.walls)}", ""]
    except Exception as exc:
        lines += [f"Nije dostupno: {exc}", ""]
    lines += ["TERMIKA"]
    try:
        thermal = to_thermal_input(model)
        known = sum(1 for wall in thermal.walls if wall.thermal_conductivity_w_mk and wall.thermal_conductivity_w_mk > 0)
        lines += [f"Zidovi: {len(thermal.walls)}", f"Verificirana λ svojstva: {known}/{len(thermal.walls)}", ""]
    except Exception as exc:
        lines += [f"Nije dostupno: {exc}", ""]
    lines += ["KOLIČINE", f"Prostorije: {len(q.rooms)}", f"Zidovi: {len(q.walls)}", f"Otvori: {len(q.openings)}", f"Stepeništa: {len(q.stairs)}", f"Terase: {len(q.terraces)}", f"Površina prostorija: {sum(r.floor_area_m2 for r in q.rooms):.2f} m²", f"Volumen prostorija: {sum(r.volume_m3 for r in q.rooms):.2f} m³", ""]
    lines += ["MEP", f"Ventilacija: {len(registry.all_ventilation_openings)}", f"Voda: {len(registry.all_water_branches)}", f"Grijanje: {len(registry.all_heating_zones)}", ""]
    lines += ["MODEL INTEGRITET", f"Leveli: {len(model.levels)}", f"Materijali/Proizvodi: {len(model.materials)}", "Jedan BuildingModel je source of truth za sve navedene prikaze."]
    widget.configure(state="normal"); widget.delete("1.0", "end"); widget.insert("1.0", "\n".join(lines)); widget.configure(state="disabled")


def _init_with_reference_house(self: CompleteBuildingWorkspaceApp) -> None:
    _original_init(self)
    self.open_reference_house()
    _install_engineering_summary(self)


def run_gui_acceptance() -> None:
    """Run the deterministic visual acceptance path inside the packaged EXE."""
    app = CompleteBuildingWorkspaceApp()
    try:
        app.open_reference_house()
        assert app.workflow.model.levels, "Reference House: no levels"
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
        if not app.workflow.model.materials:
            raise RuntimeError("Materijali: canonical Material/Product registry is empty")
        print("GUI ACCEPTANCE GREEN: Reference House -> Tlocrt -> Presjek -> 3D -> Provjera -> Izvještaj -> Materijali")
    finally:
        app.destroy()


CompleteBuildingWorkspaceApp.__init__ = _init_with_reference_house
CompleteBuildingWorkspaceApp._build_model_tab = _build_model_tab_with_inspector
CompleteBuildingWorkspaceApp.show_canonical_model_inspector = show_canonical_model_inspector
CompleteBuildingWorkspaceApp.draw_floor_plan = _draw_floor_plan_with_elements
CompleteBuildingWorkspaceApp.refresh_engineering_summary = refresh_engineering_summary


def main() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") == "1":
        run_gui_acceptance()
        return
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
