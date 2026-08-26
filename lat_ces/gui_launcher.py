"""Production desktop launcher with a visible canonical BuildingModel inspector."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.gui_complete import CompleteBuildingWorkspaceApp


_original_build_model_tab = CompleteBuildingWorkspaceApp._build_model_tab


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
    """Show canonical Room/Wall/Opening/Material records from the same model."""
    window = tk.Toplevel(self)
    window.title("LAT-CES — Canonical Building Model")
    window.geometry("1050x620")
    window.transient(self)

    ttk.Label(
        window,
        text="Canonical BuildingModel — jedan fizički model / mnogo stručnih pogleda",
        font=("Segoe UI", 12, "bold"),
    ).pack(anchor="w", padx=12, pady=(10, 6))

    tree = ttk.Treeview(
        window,
        columns=("kind", "id", "details"),
        show="headings",
    )
    tree.heading("kind", text="Objekat")
    tree.heading("id", text="ID")
    tree.heading("details", text="Podaci")
    tree.column("kind", width=110, anchor="w")
    tree.column("id", width=330, anchor="w")
    tree.column("details", width=560, anchor="w")
    tree.pack(fill="both", expand=True, padx=12, pady=6)

    model = self.workflow.model
    for level in model.levels.values():
        _add_record(
            tree,
            "Level",
            level.level_id,
            f"{level.name} · {level.length_m:.2f} × {level.width_m:.2f} m · h={level.height:.2f} m",
        )
        for room in level.rooms.values():
            _add_record(
                tree,
                "Room",
                room.room_id,
                f"{room.name} · {room.floor_area:.2f} m² · V={room.volume:.2f} m³ · h={room.footprint.height:.2f} m",
            )
        if level.floor_plan:
            for wall in level.floor_plan.walls.values():
                product = model.materials.get(wall.material_id) if wall.material_id else None
                product_name = product.name if product else "N/A"
                _add_record(
                    tree,
                    "Wall",
                    wall.wall_id,
                    f"{wall.name} · {'vanjski' if wall.exterior else 'unutrašnji'} · "
                    f"{'nosivi' if wall.load_bearing else 'pregradni'} · Product={product_name}",
                )
                for opening in wall.openings:
                    _add_record(
                        tree,
                        "Opening",
                        opening.opening_id,
                        f"{opening.kind} · {opening.width:.2f} × {opening.height_m:.2f} m · wall={wall.wall_id}",
                    )
    for material in model.materials.values():
        dimensions = " × ".join(f"{value:.3f}" for value in material.dimensions_m)
        product_id = material.product_id or "N/A"
        density = "N/A" if material.density is None else f"{material.density:.1f} kg/m³"
        lam = "N/A" if material.thermal_conductivity is None else f"{material.thermal_conductivity:.3f} W/mK"
        manufacturer = getattr(material, "manufacturer", None) or "N/A"
        _add_record(
            tree,
            "Material/Product",
            material.material_id,
            f"{material.name} · Product={product_id} · dim={dimensions} · ρ={density} · λ={lam} · proizvođač={manufacturer}",
        )


CompleteBuildingWorkspaceApp._build_model_tab = _build_model_tab_with_inspector
CompleteBuildingWorkspaceApp.show_canonical_model_inspector = show_canonical_model_inspector


def main() -> None:
    CompleteBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
