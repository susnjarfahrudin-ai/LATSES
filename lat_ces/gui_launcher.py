"""Production desktop launcher with a visible canonical BuildingModel inspector."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.building.floor_plan import Point2D
from lat_ces.building.structural import calculate_structural_loads
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.thermal.building_model_adapter import to_thermal_input


_original_init = CompleteBuildingWorkspaceApp.__init__
_original_build_model_tab = CompleteBuildingWorkspaceApp._build_model_tab
_original_draw_floor_plan = CompleteBuildingWorkspaceApp.draw_floor_plan


def _build_model_tab_with_inspector(self: CompleteBuildingWorkspaceApp, tab: ttk.Frame) -> None:
    _original_build_model_tab(self, tab)
    ttk.Button(
        tab,
        text="Model Inspector",
        command=self.show_canonical_model_inspector,
    ).pack(side="left", padx=(10, 2))


def _add_record(tree: ttk.Treeview, kind: str, object_id: str, details: str) -> None:
    tree.insert("", "end", values=(kind, object_id, details))


def show_canonical_model_inspector(self: CompleteBuildingWorkspaceApp) -> None:
    """Show canonical Room/Wall/Opening/Stair/Terrace/Material records from the same model."""
    window = tk.Toplevel(self)
    window.title("LAT-CES — Canonical Building Model")
    window.geometry("1050x620")
    window.transient(self)

    ttk.Label(
        window,
        text="Canonical BuildingModel — jedan fizički model / mnogo stručnih pogleda",
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w", padx=12, pady=(10, 6))

    tree = ttk.Treeview(window, columns=("kind", "id", "details"), show="headings")
    tree.heading("kind", text="Objekat")
    tree.heading("id", text="ID")
    tree.heading("details", text="Podaci")
    tree.column("kind", width=130, anchor="w")
    tree.column("id", width=330, anchor="w")
    tree.column("details", width=550, anchor="w")
    tree.pack(fill="both", expand=True, padx=12, pady=6)

    model = self.workflow.model
    for level in model.levels.values():
        _add_record(tree, "Level", level.level_id, f"{level.name} · {level.length_m:.2f} × {level.width_m:.2f} m · h={level.height:.2f} m")
        for room in level.rooms.values():
            _add_record(tree, "Room", room.room_id, f"{room.name} · {room.floor_area:.2f} m² · V={room.volume:.2f} m³ · h={room.footprint.height:.2f} m")
        for stair in level.stairs.values():
            material = model.materials.get(stair.material_id) if getattr(stair, "material_id", None) else None
            product = material.resolved_product_id if material else "N/A"
            _add_record(
                tree,
                "Stair",
                stair.id,
                f"{stair.name} · {stair.length_m:.2f} × {stair.width_m:.2f} m · step={stair.riser_count or 'N/A'} · h={stair.riser_height_m or 'N/A'} m · gazište={stair.tread_width_m or 'N/A'} m · landing={'DA' if stair.landing else 'NE'} · ograda={'DA' if stair.railing else 'NE'} · otvor={'DA' if stair.floor_opening else 'NE'} · Product={product}",
            )
        for terrace in level.terraces.values():
            material = model.materials.get(terrace.material_id) if getattr(terrace, "material_id", None) else None
            product = material.resolved_product_id if material else "N/A"
            _add_record(tree, "Terrace", terrace.id, f"{terrace.name} · {terrace.length_m:.2f} × {terrace.width_m:.2f} m · konstrukcija={terrace.construction_type} · Product={product}")
        if level.floor_plan:
            for wall in level.floor_plan.walls.values():
                product = model.materials.get(wall.material_id) if wall.material_id else None
                product_name = product.name if product else "N/A"
                _add_record(tree, "Wall", wall.wall_id, f"{wall.name} · {'vanjski' if wall.exterior else 'unutrašnji'} · {'nosivi' if wall.load_bearing else 'pregradni'} · Product={product_name}")
                for opening in wall.openings:
                    _add_record(tree, "Opening", opening.opening_id, f"{opening.kind} · {opening.width:.2f} × {opening.height_m:.2f} m · wall={wall.wall_id}")
    for material in model.materials.values():
        dimensions = " × ".join(f"{value:.3f}" for value in material.dimensions_m)
        product_id = material.resolved_product_id
        density = "N/A" if material.density is None else f"{material.density:.1f} kg/m³"
        lam = "N/A" if material.thermal_conductivity is None else f"{material.thermal_conductivity:.3f} W/mK"
        manufacturer = getattr(material, "manufacturer", None) or "N/A"
        _add_record(tree, "Material/Product", material.material_id, f"{material.name} · Product={product_id} · dim={dimensions} · ρ={density} · λ={lam} · proizvođač={manufacturer}")


def _draw_canonical_elements(self: CompleteBuildingWorkspaceApp) -> None:
    """Overlay first-class rooms, stair and terrace footprints on the canonical floor plan."""
    level = self.active_level
    for room in level.rooms.values():
        footprint = room.footprint
        p1 = self.model_to_canvas(Point2D(footprint.origin.x, footprint.origin.y))
        p2 = self.model_to_canvas(Point2D(footprint.origin.x + footprint.length, footprint.origin.y))
        p3 = self.model_to_canvas(Point2D(footprint.origin.x + footprint.length, footprint.origin.y + footprint.width))
        p4 = self.model_to_canvas(Point2D(footprint.origin.x, footprint.origin.y + footprint.width))
        self.canvas.create_rectangle(min(p1[0], p3[0]), min(p1[1], p3[1]), max(p1[0], p3[0]), max(p1[1], p3[1]), outline="#64748b", width=1)
        self.canvas.create_text((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2, text=room.name, fill="#374151", font=("Segoe UI", 9, "bold"))
    for stair in level.stairs.values():
        footprint = stair.footprint
        p1 = self.model_to_canvas(Point2D(footprint.origin.x, footprint.origin.y))
        p2 = self.model_to_canvas(Point2D(footprint.origin.x + footprint.length, footprint.origin.y))
        p3 = self.model_to_canvas(Point2D(footprint.origin.x + footprint.length, footprint.origin.y + footprint.width))
        p4 = self.model_to_canvas(Point2D(footprint.origin.x, footprint.origin.y + footprint.width))
        self.canvas.create_polygon(p1, p2, p3, p4, outline="#2563eb", fill="#dbeafe", width=2, stipple="gray25")
        self.canvas.create_text((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2, text=f"Stepenište\n{stair.riser_count or ''}".strip(), fill="#1d4ed8")
    for terrace in level.terraces.values():
        footprint = terrace.footprint
        p1 = self.model_to_canvas(Point2D(footprint.origin.x, footprint.origin.y))
        p2 = self.model_to_canvas(Point2D(footprint.origin.x + footprint.length, footprint.origin.y))
        p3 = self.model_to_canvas(Point2D(footprint.origin.x + footprint.length, footprint.origin.y + footprint.width))
        p4 = self.model_to_canvas(Point2D(footprint.origin.x, footprint.origin.y + footprint.width))
        self.canvas.create_polygon(p1, p2, p3, p4, outline="#b45309", fill="#fef3c7", width=2, stipple="gray25")
        self.canvas.create_text((p1[0] + p3[0]) / 2, (p1[1] + p3[1]) / 2, text="Terasa", fill="#92400e")


def _draw_floor_plan_with_elements(self: CompleteBuildingWorkspaceApp) -> None:
    _original_draw_floor_plan(self)
    _draw_canonical_elements(self)


def _install_engineering_summary(self: CompleteBuildingWorkspaceApp) -> None:
    if not hasattr(self, "complete_tabs"):
        return
    frame = ttk.Frame(self.complete_tabs, padding=10)
    self.complete_tabs.add(frame, text="Engineering Summary")
    toolbar = ttk.Frame(frame)
    toolbar.pack(fill="x")
    ttk.Button(toolbar, text="Osvježi statiku/termiku", command=self.refresh_engineering_summary).pack(side="left")
    self.engineering_summary = tk.Text(frame, height=18, wrap="word")
    self.engineering_summary.pack(fill="both", expand=True, pady=(8, 0))
    self.engineering_summary.configure(state="disabled")
    self.refresh_engineering_summary()


def refresh_engineering_summary(self: CompleteBuildingWorkspaceApp) -> None:
    widget = getattr(self, "engineering_summary", None)
    if widget is None or not getattr(self, "workflow", None):
        return
    model = self.workflow.model
    lines = ["CANONICAL BUILDING MODEL — ENGINEERING SUMMARY", ""]
    try:
        structural = calculate_structural_loads(model)
        lines.extend(("STATIKA", f"Status: {structural.status}", f"Ukupno vertikalno linijsko opterećenje: {structural.total_vertical_line_load_kn_m:.3f} kN/m", f"Zidova u izvještaju: {len(structural.walls)}", ""))
    except Exception as exc:
        lines.extend(("STATIKA", f"Nije dostupno: {exc}", ""))
    try:
        thermal = to_thermal_input(model)
        lines.append("TERMIKA")
        lines.append(f"Zidova: {len(thermal.walls)}")
        for wall in thermal.walls:
            if wall.thermal_conductivity_w_mk and wall.thermal_conductivity_w_mk > 0:
                resistance = wall.conductive_resistance_m2kw
                lines.append(f"{wall.wall_id}: λ={wall.thermal_conductivity_w_mk:.3f} W/mK · d={wall.thickness_m:.3f} m · R={resistance:.3f} m²K/W")
            else:
                lines.append(f"{wall.wall_id}: λ=N/A · potrebna verificirana materijalna vrijednost")
    except Exception as exc:
        lines.extend(("TERMIKA", f"Nije dostupna: {exc}"))
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", "\n".join(lines))
    widget.configure(state="disabled")


def _init_with_reference_house(self: CompleteBuildingWorkspaceApp) -> None:
    _original_init(self)
    self.open_reference_house()
    _install_engineering_summary(self)


CompleteBuildingWorkspaceApp.__init__ = _init_with_reference_house
CompleteBuildingWorkspaceApp._build_model_tab = _build_model_tab_with_inspector
CompleteBuildingWorkspaceApp.show_canonical_model_inspector = show_canonical_model_inspector
CompleteBuildingWorkspaceApp.draw_floor_plan = _draw_floor_plan_with_elements
CompleteBuildingWorkspaceApp.refresh_engineering_summary = refresh_engineering_summary


def main() -> None:
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
