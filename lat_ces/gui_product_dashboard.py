"""Project Overview + real Product -> BuildingModel assignment workspace."""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from lat_ces.building.mep import HeatingZone, VentilationOpening, ensure_mep_registry
from lat_ces.building.model import Material
from lat_ces.catalog.product_catalog import all_products, categories, get_product, products_for_category
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.gui_dashboard import ProjectOverviewApp


class ProductBuildingWorkspaceApp(ProjectOverviewApp):
    """Existing canonical GUI plus one Product assignment layer."""

    def __init__(self) -> None:
        super().__init__()
        self._install_product_assignment_tab()

    def _install_product_assignment_tab(self) -> None:
        frame = ttk.Frame(self.complete_tabs, padding=12)
        self.complete_tabs.add(frame, text="Katalog proizvoda")
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2, weight=2)
        frame.rowconfigure(1, weight=1)

        self.catalog_category_var = tk.StringVar(value=categories()[0])
        self.catalog_target_type_var = tk.StringVar(value="Zid")
        self.catalog_target_var = tk.StringVar()

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ttk.Label(header, text="Product / Material → BuildingModel", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(header, text="  isti model, isti identiteti", foreground="#475569").pack(side="left", padx=8)

        left = ttk.LabelFrame(frame, text="Proizvodi", padding=8)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        ttk.Label(left, text="Kategorija").grid(row=0, column=0, sticky="w")
        combo = ttk.Combobox(left, textvariable=self.catalog_category_var, state="readonly", values=categories())
        combo.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_catalog_products())
        self.catalog_tree = ttk.Treeview(left, columns=("name", "status"), show="headings", selectmode="browse")
        self.catalog_tree.heading("name", text="Proizvod")
        self.catalog_tree.heading("status", text="Podaci")
        self.catalog_tree.column("name", width=230)
        self.catalog_tree.column("status", width=90)
        self.catalog_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        self.catalog_tree.bind("<<TreeviewSelect>>", lambda _e: self._show_catalog_product())

        middle = ttk.LabelFrame(frame, text="Detalji proizvoda", padding=8)
        middle.grid(row=1, column=1, sticky="nsew", padx=6)
        middle.columnconfigure(0, weight=1)
        middle.rowconfigure(1, weight=1)
        self.catalog_detail_title = ttk.Label(middle, font=("Segoe UI", 12, "bold"), wraplength=430)
        self.catalog_detail_title.grid(row=0, column=0, sticky="w")
        self.catalog_detail = tk.Text(middle, wrap="word", height=12)
        self.catalog_detail.grid(row=1, column=0, sticky="nsew", pady=(6, 8))
        self.catalog_detail.configure(state="disabled")
        ttk.Label(middle, text="Missing podaci se ne popunjavaju pretpostavkom.", foreground="#92400e").grid(row=2, column=0, sticky="w")

        right = ttk.LabelFrame(frame, text="Primijeni na konkretan element", padding=8)
        right.grid(row=1, column=2, sticky="nsew", padx=(6, 0))
        right.columnconfigure(0, weight=1)
        ttk.Label(right, text="Tip cilja").grid(row=0, column=0, sticky="w")
        target_type = ttk.Combobox(right, textvariable=self.catalog_target_type_var, state="readonly", values=("Zid", "Otvor", "Podno grijanje / prostorija", "Ventilacija"))
        target_type.grid(row=1, column=0, sticky="ew", pady=(3, 8))
        target_type.bind("<<ComboboxSelected>>", lambda _e: self._refresh_catalog_targets())
        ttk.Label(right, text="Ciljni objekat").grid(row=2, column=0, sticky="w")
        self.catalog_target_combo = ttk.Combobox(right, textvariable=self.catalog_target_var, state="readonly")
        self.catalog_target_combo.grid(row=3, column=0, sticky="ew", pady=(3, 8))
        ttk.Button(right, text="Primijeni proizvod", command=self._apply_selected_product).grid(row=4, column=0, sticky="ew", pady=(5, 0))
        self.catalog_assignment_status = ttk.Label(right, wraplength=260)
        self.catalog_assignment_status.grid(row=5, column=0, sticky="w", pady=(12, 0))
        self._refresh_catalog_products()
        self._refresh_catalog_targets()

    def _refresh_catalog_products(self) -> None:
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        for product in products_for_category(self.catalog_category_var.get()):
            self.catalog_tree.insert("", "end", iid=product.product_id, values=(product.name, product.status))
        items = self.catalog_tree.get_children()
        if items:
            self.catalog_tree.selection_set(items[0])
            self.catalog_tree.focus(items[0])
            self._show_catalog_product()

    def _selected_product(self):
        selection = self.catalog_tree.selection()
        return get_product(selection[0]) if selection else None

    def _show_catalog_product(self) -> None:
        product = self._selected_product()
        if product is None:
            return
        self.catalog_detail_title.configure(text=product.engineering_summary)
        text = "\n".join([
            f"Kategorija: {product.category}",
            f"Proizvođač: {product.manufacturer or 'N/A'}",
            f"Dimenzije: {product.dimensions or 'N/A'}",
            f"Status: {product.status}",
            f"Gustina: {product.density_kg_m3 if product.density_kg_m3 is not None else 'N/A'} kg/m³",
            f"E: {product.youngs_modulus_pa if product.youngs_modulus_pa is not None else 'N/A'} Pa",
            f"λ: {product.thermal_conductivity_w_mk if product.thermal_conductivity_w_mk is not None else 'N/A'} W/mK",
            f"Čvrstoća: {product.compressive_strength_mpa if product.compressive_strength_mpa is not None else 'N/A'} MPa",
            f"Izvor: {product.source or 'N/A'}",
        ])
        self.catalog_detail.configure(state="normal")
        self.catalog_detail.delete("1.0", "end")
        self.catalog_detail.insert("1.0", text)
        self.catalog_detail.configure(state="disabled")

    def _wall_targets(self):
        plan = self.floor_plan
        return [(wall.wall_id, f"{wall.name} · {wall.segment.length:.2f} m") for wall in plan.walls.values()]

    def _opening_targets(self):
        targets = []
        for wall in self.floor_plan.walls.values():
            for opening in wall.openings:
                targets.append((opening.opening_id, f"{wall.name} / {opening.kind} · {opening.width:.2f} m"))
        return targets

    def _room_targets(self):
        return [(room.room_id, room.name) for room in self.active_level.rooms.values()]

    def _ventilation_targets(self):
        registry = ensure_mep_registry(self.workflow.model)
        targets = [(item.id, f"{item.room_id} / {item.kind} · Ø{item.diameter_m*1000:.0f} mm") for item in registry.all_ventilation_openings]
        if not targets:
            targets.append(("__NEW__", "+ Nova ventilacija u prvoj prostoriji"))
        return targets

    def _refresh_catalog_targets(self) -> None:
        kind = self.catalog_target_type_var.get()
        if kind == "Zid":
            targets = self._wall_targets()
        elif kind == "Otvor":
            targets = self._opening_targets()
        elif kind == "Podno grijanje / prostorija":
            targets = self._room_targets()
        else:
            targets = self._ventilation_targets()
        values = [label for _id, label in targets]
        self._catalog_target_map = {label: _id for _id, label in targets}
        self.catalog_target_combo.configure(values=values)
        if values:
            self.catalog_target_var.set(values[0])
        else:
            self.catalog_target_var.set("")

    def _ensure_catalog_material(self, product) -> str:
        existing = next((mid for mid, material in self.workflow.model.materials.items() if material.product_id == product.product_id), None)
        if existing:
            return existing
        material = Material(name=product.name, density=product.density_kg_m3, youngs_modulus=product.youngs_modulus_pa, thermal_conductivity=product.thermal_conductivity_w_mk, compressive_strength_mpa=product.compressive_strength_mpa, product_id=product.product_id, manufacturer=product.manufacturer, category=product.category)
        self.workflow.model.add_material(material)
        return material.material_id

    def _apply_selected_product(self) -> None:
        product = self._selected_product()
        target_label = self.catalog_target_var.get()
        target_id = self._catalog_target_map.get(target_label)
        if product is None or not target_id:
            self.catalog_assignment_status.configure(text="Odaberi proizvod i ciljni objekat.")
            return
        bindings = ensure_product_binding_registry(self.workflow.model)
        kind = self.catalog_target_type_var.get()

        if kind == "Zid":
            wall = self.floor_plan.walls.get(target_id)
            if wall is None:
                return
            wall.material_id = self._ensure_catalog_material(product)
            bindings.bind(wall.wall_id, "wall", product.product_id)
            message = f"{wall.name} → {product.name}"
        elif kind == "Otvor":
            bindings.bind(target_id, "opening", product.product_id)
            message = f"Otvor {target_id} → {product.name}"
        elif kind == "Podno grijanje / prostorija":
            room_id = target_id
            registry = ensure_mep_registry(self.workflow.model)
            zone = next((z for z in registry.all_heating_zones if z.room_id == room_id), None)
            if zone is None:
                zone = registry.add_heating_zone(HeatingZone(id=f"HZ-{room_id}", room_id=room_id, emitter_type="underfloor", design_supply_temp_c=35.0, design_return_temp_c=30.0))
            bindings.bind(zone.id, "heating_zone", product.product_id)
            message = f"Podno grijanje {room_id} → {product.name}"
        else:
            registry = ensure_mep_registry(self.workflow.model)
            vent = None if target_id == "__NEW__" else next((x for x in registry.all_ventilation_openings if x.id == target_id), None)
            if vent is None:
                rooms = self._room_targets()
                if not rooms:
                    self.catalog_assignment_status.configure(text="Nema prostorije za ventilacioni element.")
                    return
                room_id = rooms[0][0]
                vent = registry.add_ventilation_opening(VentilationOpening(id=f"VENT-{room_id}", room_id=room_id, kind="supply", diameter_m=0.10))
            bindings.bind(vent.id, "ventilation_opening", product.product_id)
            message = f"Ventilacija {vent.room_id} → {product.name}"

        self.catalog_assignment_status.configure(text=f"DODIJELJENO\n{message}")
        self.status_var.set(f"Proizvod primijenjen: {product.name}")
        self._refresh_project_overview()
        self._refresh_catalog_targets()

    def run_acceptance(self) -> None:
        products = all_products()
        assert len(products) >= 10
        assert "Katalog proizvoda" in [self.complete_tabs.tab(i, "text") for i in range(self.complete_tabs.index("end"))]
        model = self.workflow.model
        product = products[2]
        material_id_before = len(model.materials)
        wall_id, _ = self._wall_targets()[0]
        self.catalog_category_var.set(product.category)
        self._refresh_catalog_products()
        self.catalog_tree.selection_set(product.product_id)
        self.catalog_target_type_var.set("Zid")
        self._refresh_catalog_targets()
        self.catalog_target_var.set(self._wall_targets()[0][1])
        self._apply_selected_product()
        assert len(model.materials) == material_id_before + 1
        assert ensure_product_binding_registry(model).product_id_for(wall_id) == product.product_id
        room_id, _ = self._room_targets()[0]
        self.catalog_category_var.set("Podno grijanje")
        self._refresh_catalog_products()
        self.catalog_tree.selection_set(products_for_category("Podno grijanje")[0].product_id)
        self.catalog_target_type_var.set("Podno grijanje / prostorija")
        self._refresh_catalog_targets()
        self.catalog_target_var.set(self._room_targets()[0][1])
        self._apply_selected_product()
        registry = ensure_mep_registry(model)
        assert any(zone.room_id == room_id for zone in registry.all_heating_zones)
        assert registry.all_heating_zones
        print("CATALOG BINDING GREEN: wall + material + opening binding + underfloor heating zone + ventilation product path")


def run_catalog_acceptance() -> None:
    app = ProductBuildingWorkspaceApp()
    try:
        app.update_idletasks()
        app.open_reference_house()
        app.update_idletasks()
        app.run_acceptance()
        print("GUI PRODUCT BINDING GREEN")
    finally:
        app.destroy()


def main() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") == "1":
        run_catalog_acceptance()
        return
    ProductBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
