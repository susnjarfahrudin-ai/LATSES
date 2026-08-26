"""Visible GUI binding for the canonical BuildingModel.

This layer adds inspection only: it never creates a second Room/Wall/Material model.
All displayed values are read directly from CompleteBuildingWorkspaceApp.workflow.model.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.building.model import BuildingModel
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp


def build_model_inspector_records(model: BuildingModel) -> tuple[dict[str, object], ...]:
    """Return deterministic, read-only inspection records from the canonical model."""
    records: list[dict[str, object]] = []
    for level in model.levels.values():
        records.append(
            {
                "kind": "level",
                "id": level.level_id,
                "name": level.name,
                "parent_id": None,
                "details": {
                    "Naziv": level.name,
                    "ID": level.level_id,
                    "Visina": f"{level.height:.3f} m",
                    "Kotа": f"{level.elevation:.3f} m",
                    "Prostorije": str(len(level.rooms)),
                    "Stepenice": str(len(level.stairs)),
                    "Terase": str(len(level.terraces)),
                },
            }
        )
        for room in level.rooms.values():
            records.append(
                {
                    "kind": "room",
                    "id": room.room_id,
                    "name": room.name,
                    "parent_id": level.level_id,
                    "details": {
                        "Naziv": room.name,
                        "ID": room.room_id,
                        "Dužina": f"{room.footprint.length:.3f} m",
                        "Širina": f"{room.footprint.width:.3f} m",
                        "Visina": f"{room.footprint.height:.3f} m",
                        "Površina": f"{room.floor_area:.3f} m²",
                        "Volumen": f"{room.volume:.3f} m³",
                    },
                }
            )
        if level.floor_plan:
            for wall in level.floor_plan.walls.values():
                material = model.materials.get(wall.material_id) if wall.material_id else None
                records.append(
                    {
                        "kind": "wall",
                        "id": wall.wall_id,
                        "name": wall.name,
                        "parent_id": level.level_id,
                        "details": {
                            "Naziv": wall.name,
                            "ID": wall.wall_id,
                            "Tip": "Vanjski" if wall.exterior else "Unutrašnji",
                            "Nosivost": "Nosivi" if wall.load_bearing else "Pregradni",
                            "Debljina": f"{wall.thickness:.3f} m",
                            "Product ID": material.resolved_product_id if material else "N/A",
                            "Proizvođač": material.manufacturer or "N/A" if material else "N/A",
                            "Materijal": material.name if material else "Nije definisan",
                        },
                    }
                )
                for opening in wall.openings:
                    records.append(
                        {
                            "kind": "opening",
                            "id": opening.opening_id,
                            "name": f"{opening.kind} — {opening.opening_id}",
                            "parent_id": wall.wall_id,
                            "details": {
                                "Tip": opening.kind,
                                "ID": opening.opening_id,
                                "Širina": f"{opening.width:.3f} m",
                                "Visina": f"{opening.height_m:.3f} m",
                                "Površina": f"{opening.width * opening.height_m:.3f} m²",
                                "Zid ID": wall.wall_id,
                            },
                        }
                    )
        for stair_id, stair in level.stairs.items():
            records.append(
                {
                    "kind": "stair",
                    "id": str(stair_id),
                    "name": "Stepenice",
                    "parent_id": level.level_id,
                    "details": {"Tip": "Stepenice", "ID": str(stair_id)},
                }
            )
        for terrace_id, terrace in level.terraces.items():
            records.append(
                {
                    "kind": "terrace",
                    "id": str(terrace_id),
                    "name": "Terasa",
                    "parent_id": level.level_id,
                    "details": {"Tip": "Terasa", "ID": str(terrace_id)},
                }
            )
    for material in model.materials.values():
        records.append(
            {
                "kind": "material",
                "id": material.resolved_product_id,
                "name": material.name,
                "parent_id": None,
                "details": {
                    "Naziv": material.name,
                    "Material ID": material.material_id,
                    "Product ID": material.resolved_product_id,
                    "Proizvođač": material.manufacturer or "Nije definisan",
                    "Gustina": f"{material.density:.3f} kg/m³" if material.density is not None else "Nije definisana",
                    "λ": f"{material.thermal_conductivity:.5f} W/mK" if material.thermal_conductivity is not None else "Nije definisana",
                    "Čvrstoća": f"{material.compressive_strength_mpa:.3f} MPa" if material.compressive_strength_mpa is not None else "Nije definisana",
                    "Dimenzije": " × ".join(f"{value:.3f} m" for value in material.dimensions_m) if material.dimensions_m else "Nisu definisane",
                },
            }
        )
    return tuple(records)


class BuildingModelBoundWorkspaceApp(CompleteBuildingWorkspaceApp):
    """Existing desktop workspace with a visible canonical-model inspector."""

    def __init__(self) -> None:
        self._model_inspector_tree: ttk.Treeview | None = None
        self._model_inspector_details: tk.Text | None = None
        self._model_inspector_items: dict[str, dict[str, object]] = {}
        super().__init__()
        self._install_model_inspector()
        self._refresh_model_inspector()

    def _install_model_inspector(self) -> None:
        if not hasattr(self, "complete_tabs"):
            return
        frame = ttk.Frame(self.complete_tabs, padding=8)
        self.complete_tabs.add(frame, text="Model / Identitet")

        splitter = ttk.Panedwindow(frame, orient="horizontal")
        splitter.pack(fill="both", expand=True)

        left = ttk.Frame(splitter, padding=(0, 0, 8, 0))
        right = ttk.LabelFrame(splitter, text="Podaci iz canonical BuildingModel", padding=8)
        splitter.add(left, weight=1)
        splitter.add(right, weight=1)

        self._model_inspector_tree = ttk.Treeview(left, columns=("kind", "id"), show="tree headings", height=12)
        self._model_inspector_tree.heading("#0", text="Objekat")
        self._model_inspector_tree.heading("kind", text="Tip")
        self._model_inspector_tree.heading("id", text="ID")
        self._model_inspector_tree.column("#0", width=220, anchor="w")
        self._model_inspector_tree.column("kind", width=100, anchor="w")
        self._model_inspector_tree.column("id", width=260, anchor="w")
        self._model_inspector_tree.pack(fill="both", expand=True)
        self._model_inspector_tree.bind("<<TreeviewSelect>>", self._on_model_inspector_select)

        self._model_inspector_details = tk.Text(right, height=12, wrap="word")
        self._model_inspector_details.pack(fill="both", expand=True)
        self._model_inspector_details.configure(state="disabled")

        ttk.Label(
            frame,
            text="Ovaj prikaz samo čita canonical BuildingModel; prikazani ID-ovi su isti za statiku, termiku, MEP i količine.",
            wraplength=900,
        ).pack(fill="x", pady=(8, 0))

    def _refresh_model_inspector(self) -> None:
        tree = self._model_inspector_tree
        if tree is None or not getattr(self, "workflow", None):
            return
        records = build_model_inspector_records(self.workflow.model)
        tree.delete(*tree.get_children())
        self._model_inspector_items.clear()

        roots: dict[str, str] = {}
        for record in records:
            if record["kind"] == "level":
                item = tree.insert("", "end", text=record["name"], values=(record["kind"], record["id"]), open=True)
                roots[str(record["id"])] = item
                self._model_inspector_items[item] = record
        for record in records:
            parent_id = record["parent_id"]
            if parent_id is None or record["kind"] == "level":
                continue
            parent_item = next((item_id for item_id, value in self._model_inspector_items.items() if value["id"] == parent_id), None)
            if parent_item is None:
                parent_item = roots.get(str(parent_id), "")
            item = tree.insert(parent_item, "end", text=record["name"], values=(record["kind"], record["id"]))
            self._model_inspector_items[item] = record

        for record in records:
            if record["kind"] == "material":
                item = tree.insert("", "end", text=record["name"], values=(record["kind"], record["id"]))
                self._model_inspector_items[item] = record

    def _on_model_inspector_select(self, _event=None) -> None:
        tree = self._model_inspector_tree
        details = self._model_inspector_details
        if tree is None or details is None:
            return
        selection = tree.selection()
        if not selection:
            return
        record = self._model_inspector_items.get(selection[0])
        if record is None:
            return
        lines = [f"{record['name']}", "", *[f"{key}: {value}" for key, value in record["details"].items()]]
        details.configure(state="normal")
        details.delete("1.0", "end")
        details.insert("1.0", "\n".join(lines))
        details.configure(state="disabled")

    def _refresh_complete_tabs(self):
        super()._refresh_complete_tabs()
        self._refresh_model_inspector()

    def refresh_view(self):
        super().refresh_view()
        self._refresh_model_inspector()


def main() -> None:
    BuildingModelBoundWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
