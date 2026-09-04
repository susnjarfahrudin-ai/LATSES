"""Master desktop shell over the canonical CompleteBuildingWorkspaceApp."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.gui_theme import COLORS, apply_latces_theme
from lat_ces.materials.building_catalog import BuildingMaterialCatalog
from lat_ces.visualization_3d_adapter import to_building_scene_3d


class MasterBuildingWorkspaceApp(CompleteBuildingWorkspaceApp):
    """Single desktop shell with a shared theme and parameterized catalog."""

    def __init__(self) -> None:
        super().__init__()
        apply_latces_theme(self)
        self.catalog = BuildingMaterialCatalog.default()
        self._install_catalog_tab()
        self._install_3d_tab()

    def _install_3d_tab(self) -> None:
        tab = ttk.Frame(self.complete_tabs, padding=10)
        self.complete_tabs.add(tab, text="3D")
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Label(toolbar, text="Canonical BuildingModel · read-only 3D").pack(side="left")
        ttk.Button(toolbar, text="Osvježi", style="LATCES.Secondary.TButton", command=self._refresh_3d_view).pack(side="right")
        self.canvas_3d = tk.Canvas(tab, background="#f6fbfe", highlightthickness=1, highlightbackground="#a9c9dc")
        self.canvas_3d.pack(fill="both", expand=True)
        self.canvas_3d.bind("<Configure>", lambda _event: self._refresh_3d_view())
        self._refresh_3d_view()

    def _refresh_3d_view(self) -> None:
        canvas = getattr(self, "canvas_3d", None)
        if canvas is None or not getattr(self, "workflow", None):
            return
        scene = to_building_scene_3d(self.workflow.model)
        canvas.delete("all")
        width = max(canvas.winfo_width(), 700)
        height = max(canvas.winfo_height(), 450)
        objects = [obj for obj in scene.objects if obj.element_type == "wall"]
        if not objects:
            canvas.create_text(width / 2, height / 2, text="3D — BuildingModel nema zidove za prikaz", font=("Segoe UI", 13, "bold"))
            return
        xs = [obj.geometry.origin_x_m for obj in objects]
        ys = [obj.geometry.origin_y_m for obj in objects]
        xe = [obj.geometry.origin_x_m + obj.geometry.length_m for obj in objects]
        ye = [obj.geometry.origin_y_m + obj.geometry.width_m for obj in objects]
        xmin, xmax = min(xs), max(xe)
        ymin, ymax = min(ys), max(ye)
        span = max(xmax - xmin, ymax - ymin, 1.0)
        scale = min((width - 140) / span, (height - 140) / span)

        def project(x: float, y: float, z: float) -> tuple[float, float]:
            px = 70 + (x - xmin) * scale + (y - ymin) * scale * 0.45
            py = height - 70 - (x - xmin) * scale * 0.30 - (y - ymin) * scale * 0.30 - z * scale * 0.85
            return px, py

        for obj in objects:
            g = obj.geometry
            import math
            angle = math.radians(g.rotation_z_deg)
            ux, uy = math.cos(angle), math.sin(angle)
            vx, vy = -uy * g.width_m, ux * g.width_m
            corners = (
                (g.origin_x_m, g.origin_y_m, g.origin_z_m),
                (g.origin_x_m + ux * g.length_m, g.origin_y_m + uy * g.length_m, g.origin_z_m),
                (g.origin_x_m + ux * g.length_m + vx, g.origin_y_m + uy * g.length_m + vy, g.origin_z_m),
                (g.origin_x_m + vx, g.origin_y_m + vy, g.origin_z_m),
                (g.origin_x_m, g.origin_y_m, g.origin_z_m + g.height_m),
                (g.origin_x_m + ux * g.length_m, g.origin_y_m + uy * g.length_m, g.origin_z_m + g.height_m),
                (g.origin_x_m + ux * g.length_m + vx, g.origin_y_m + uy * g.length_m + vy, g.origin_z_m + g.height_m),
                (g.origin_x_m + vx, g.origin_y_m + vy, g.origin_z_m + g.height_m),
            )
            p = [project(*corner) for corner in corners]
            for a, b in ((0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)):
                canvas.create_line(*p[a], *p[b], fill="#475569", width=2)
        canvas.create_text(18, 18, text=f"3D READ-ONLY · {len(objects)} zidova · model={scene.building_model_id}", anchor="nw", font=("Segoe UI", 11, "bold"), fill="#17324d")
        canvas.create_text(18, 40, text="Izvor: to_building_scene_3d(BuildingModel) · bez izmjene modela", anchor="nw", fill="#475569")

    def _refresh_catalog_view(self) -> None:
        items = self.catalog.search(self.catalog_search_var.get())
        self.catalog_visible_items = items
        self.catalog_list.delete(0, "end")
        for item in items:
            marker = " · dimenzije obavezne" if item.requires_dimensions else ""
            self.catalog_list.insert("end", f"{item.name} [{item.unit}]{marker}")
        self._set_catalog_detail("Odaberi stavku.\n\nKategorije su parametarske: upiši stvarne mjere/proizvod nakon odabira.\nNormativni proračun ne koristi katalog kao zamjenu za projektne vrijednosti.")

    def _show_catalog_selection(self, _event=None) -> None:
        selection = self.catalog_list.curselection()
        if not selection:
            return
        item = self.catalog_visible_items[selection[0]]
        text = (
            f"ID: {item.item_id}\n"
            f"Naziv: {item.name}\n"
            f"Jedinica obračuna: {item.unit}\n"
            f"Dimenzije potrebne: {'DA' if item.requires_dimensions else 'NE'}\n\n"
            "Proračunski parametri nisu automatski izmišljeni. Za stvarni proizvod unesi ili uvezi verificirane podatke: dimenzije, gustinu, λ/U, čvrstoće, masu i proizvođača."
        )
        if item.item_id == "glazing":
            text += "\n\nStakla: " + ", ".join(option.option_id for option in self.catalog.glazing_options)
        self._set_catalog_detail(text)

    def _set_catalog_detail(self, value: str) -> None:
        self.catalog_detail.configure(state="normal")
        self.catalog_detail.delete("1.0", "end")
        self.catalog_detail.insert("1.0", value)
        self.catalog_detail.configure(state="disabled")

    def _install_catalog_tab(self) -> None:
        tab = ttk.Frame(self.complete_tabs, padding=10)
        self.complete_tabs.add(tab, text="Katalog")

        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", pady=(0, 8))
        ttk.Label(toolbar, text="Pretraga").pack(side="left")
        self.catalog_search_var = tk.StringVar()
        entry = ttk.Entry(toolbar, textvariable=self.catalog_search_var, width=38)
        entry.pack(side="left", padx=6)
        entry.bind("<KeyRelease>", lambda _event: self._refresh_catalog_view())
        ttk.Button(toolbar, text="Osvježi", style="LATCES.Secondary.TButton", command=self._refresh_catalog_view).pack(side="left")

        body = ttk.Frame(tab)
        body.pack(fill="both", expand=True)
        self.catalog_list = tk.Listbox(body, height=16, activestyle="none")
        self.catalog_list.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=self.catalog_list.yview)
        scrollbar.pack(side="left", fill="y")
        self.catalog_list.configure(yscrollcommand=scrollbar.set)

        right = ttk.LabelFrame(body, text="Odabrani element / materijal", padding=10)
        right.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.catalog_detail = tk.Text(right, height=14, wrap="word")
        self.catalog_detail.pack(fill="both", expand=True)
        self.catalog_detail.configure(state="disabled")
        self.catalog_list.bind("<<ListboxSelect>>", self._show_catalog_selection)

        status = ttk.Label(tab, text="Parametarski katalog — komercijalne dimenzije i projektne vrijednosti moraju biti verificirane.", style="LATCES.Warning.TLabel", wraplength=900)
        status.pack(fill="x", pady=(8, 0))
        self._refresh_catalog_view()


def main() -> None:
    MasterBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
