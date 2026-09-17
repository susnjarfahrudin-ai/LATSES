"""First-class product catalog UI for the canonical LAT-CES workspace."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.building.mep import HeatingZone, VentilationOpening, ensure_mep_registry
from lat_ces.building.model import Material
from lat_ces.catalog.product_binding import ensure_product_binding_registry
from lat_ces.catalog.product_catalog import all_products, categories, get_product
from lat_ces.catalog.user_store import UserProductCatalog
from lat_ces.gui_material_input import MaterialInputDialog


class ProductCatalogMixin:
    """Adds the canonical Product Catalog tab without creating another model."""

    def _install_product_catalog_tab(self) -> None:
        frame = ttk.Frame(self.complete_tabs, padding=12)
        self.complete_tabs.add(frame, text="Katalog proizvoda")
        frame.columnconfigure(0, weight=2)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2, weight=2)
        frame.rowconfigure(1, weight=1)

        self._user_product_catalog = UserProductCatalog()
        self.catalog_category_var = tk.StringVar(value=categories()[0])
        self.catalog_target_type_var = tk.StringVar(value="Zid")
        self.catalog_target_var = tk.StringVar()

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        ttk.Label(header, text="Katalog proizvoda", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(header, text="  proizvodi → BuildingModel", foreground="#475569").pack(side="left", padx=8)
        ttk.Button(header, text="Novi materijal", command=self._open_catalog_material_input).pack(side="right")

        left = ttk.LabelFrame(frame, text="Kategorija / proizvodi", padding=8)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(1, weight=1)
        ttk.Label(left, text="Kategorija").grid(row=0, column=0, sticky="w")
        category_combo = ttk.Combobox(
            left, textvariable=self.catalog_category_var, state="readonly", values=categories(), width=24
        )
        category_combo.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        category_combo.bind("<<ComboboxSelected>>", lambda _e: self._refresh_catalog_products())
        self.catalog_tree = ttk.Treeview(left, columns=("name", "status"), show="headings", selectmode="browse")
        self.catalog_tree.heading("name", text="Proizvod")
        self.catalog_tree.heading("status", text="Status")
        self.catalog_tree.column("name", width=240)
        self.catalog_tree.column("status", width=105)
        self.catalog_tree.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        self.catalog_tree.bind("<<TreeviewSelect>>", lambda _e: self._show_catalog_product())

        middle = ttk.LabelFrame(frame, text="Proizvođačka specifikacija", padding=8)
        middle.grid(row=1, column=1, sticky="nsew", padx=6)
        middle.columnconfigure(0, weight=1)
        middle.rowconfigure(1, weight=1)
        self.catalog_detail_title = ttk.Label(middle, font=("Segoe UI", 12, "bold"), wraplength=430)
        self.catalog_detail_title.grid(row=0, column=0, sticky="w")
        self.catalog_detail = tk.Text(middle, wrap="word", height=12)
        self.catalog_detail.grid(row=1, column=0, sticky="nsew", pady=(6, 8))
        self.catalog_detail.configure(state="disabled")
        ttk.Label(middle, text="USER_DECLARED = unos korisnika; nije automatski VERIFIED.", foreground="#92400e").grid(
            row=2, column=0, sticky="w"
        )

        right = ttk.LabelFrame(frame, text="Primijeni proizvod", padding=8)
        right.grid(row=1, column=2, sticky="nsew", padx=(6, 0))
        right.columnconfigure(0, weight=1)
        ttk.Label(right, text="Tip cilja").grid(row=0, column=0, sticky="w")
        target_type = ttk.Combobox(
            right,
            textvariable=self.catalog_target_type_var,
            state="readonly",
            values=("Zid", "Otvor", "Podno grijanje / prostorija", "Ventilacija"),
        )
        target_type.grid(row=1, column=0, sticky="ew", pady=(3, 8))
        target_type.bind("<<ComboboxSelected>>", lambda _e: self._refresh_catalog_targets())
        ttk.Label(right, text="Ciljni objekat").grid(row=2, column=0, sticky="w")
        self.catalog_target_combo = ttk.Combobox(right, textvariable=self.catalog_target_var, state="readonly")
        self.catalog_target_combo.grid(row=3, column=0, sticky="ew", pady=(3, 8))
        ttk.Button(right, text="Primijeni proizvod", command=self._apply_selected_catalog_product).grid(
            row=4, column=0, sticky="ew", pady=(5, 0)
        )
        self.catalog_assignment_status = ttk.Label(right, wraplength=260)
        self.catalog_assignment_status.grid(row=5, column=0, sticky="w", pady=(12, 0))
        self._refresh_catalog_products()
        self._refresh_catalog_targets()
        self._remove_legacy_material_actions()

    def _remove_legacy_material_actions(self) -> None:
        """Remove the old engineering-tab material entry point from the main GUI."""
        def walk(widget) -> None:
            for child in widget.winfo_children():
                if isinstance(child, ttk.Button) and child.cget("text") == "Novi materijal — proizvođačka specifikacija":
                    child.destroy()
                    continue
                walk(child)
        walk(self.complete_tabs)

    def _catalog_products(self):
        return all_products() + self._user_product_catalog.all_products()

    def _refresh_catalog_products(self) -> None:
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        for product in self._catalog_products():
            if product.category == self.catalog_category_var.get():
                self.catalog_tree.insert("", "end", iid=product.product_id, values=(product.name, product.status))
        items = self.catalog_tree.get_children()
        if items:
            self.catalog_tree.selection_set(items[0])
            self.catalog_tree.focus(items[0])
            self._show_catalog_product()

    def _selected_catalog_product(self):
        selection = self.catalog_tree.selection()
        if not selection:
            return None
        product_id = selection[0]
        base = get_product(product_id)
        if base is not None:
            return base
        return next((p for p in self._user_product_catalog.all_products() if p.product_id == product_id), None)

    def _show_catalog_product(self) -> None:
        product = self._selected_catalog_product()
        if product is None:
            return
        self.catalog_detail_title.configure(text=product.engineering_summary)
        text = "\n".join(
            [
                f"Kategorija: {product.category}",
                f"Proizvođač: {product.manufacturer or 'N/A'}",
                f"Product ID: {product.product_id}",
                f"Dimenzije: {product.dimensions or 'N/A'}",
                f"Status: {product.status}",
                f"Gustina: {product.density_kg_m3 if product.density_kg_m3 is not None else 'N/A'} kg/m³",
                f"E: {product.youngs_modulus_pa if product.youngs_modulus_pa is not None else 'N/A'} Pa",
                f"λ: {product.thermal_conductivity_w_mk if product.thermal_conductivity_w_mk is not None else 'N/A'} W/mK",
                f"Čvrstoća: {product.compressive_strength_mpa if product.compressive_strength_mpa is not None else 'N/A'} MPa",
                f"Izvor: {product.source or 'N/A'}",
            ]
        )
        self.catalog_detail.configure(state="normal")
        self.catalog_detail.delete("1.0", "end")
        self.catalog_detail.insert("1.0", text)
        self.catalog_detail.configure(state="disabled")

    def _open_catalog_material_input(self) -> None:
        MaterialInputDialog(self, self._add_catalog_material, category_values=categories())

    def _add_catalog_material(self, material: Material) -> None:
        product = self._user_product_catalog.add_material(material)
        self.workflow.model.add_material(material)
        self._refresh_structure_materials()
        self._refresh_catalog_products()
        self.catalog_assignment_status.configure(text=f"DODANO U KATALOG\n{product.name}")
        self.status_var.set(f"Katalog: dodat proizvod {product.name} · {product.product_id}")

    def _wall_targets(self):
        return [(wall.wall_id, f"{wall.name} · {wall.segment.length:.2f} m") for wall in self.floor_plan.walls.values()]

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
        self.catalog_target_var.set(values[0] if values else "")

    def _ensure_catalog_material(self, product) -> str:
        existing = next(
            (mid for mid, material in self.workflow.model.materials.items() if material.product_id == product.product_id),
            None,
        )
        if existing:
            return existing
        material = Material(
            name=product.name,
            density=product.density_kg_m3,
            youngs_modulus=product.youngs_modulus_pa,
            thermal_conductivity=product.thermal_conductivity_w_mk,
            compressive_strength_mpa=product.compressive_strength_mpa,
            product_id=product.product_id,
            manufacturer=product.manufacturer,
            category=product.category,
        )
        self.workflow.model.add_material(material)
        return material.material_id

    def _apply_selected_catalog_product(self) -> None:
        product = self._selected_catalog_product()
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
            registry = ensure_mep_registry(self.workflow.model)
            zone = next((z for z in registry.all_heating_zones if z.room_id == target_id), None)
            if zone is None:
                zone = registry.add_heating_zone(
                    HeatingZone(
                        id=f"HZ-{target_id}",
                        room_id=target_id,
                        emitter_type="underfloor",
                        design_supply_temp_c=35.0,
                        design_return_temp_c=30.0,
                    )
                )
            bindings.bind(zone.id, "heating_zone", product.product_id)
            message = f"Podno grijanje {target_id} → {product.name}"
        else:
            registry = ensure_mep_registry(self.workflow.model)
            vent = None if target_id == "__NEW__" else next(
                (x for x in registry.all_ventilation_openings if x.id == target_id), None
            )
            if vent is None:
                rooms = self._room_targets()
                if not rooms:
                    self.catalog_assignment_status.configure(text="Nema prostorije za ventilacioni element.")
                    return
                room_id = rooms[0][0]
                vent = registry.add_ventilation_opening(
                    VentilationOpening(id=f"VENT-{room_id}", room_id=room_id, kind="supply", diameter_m=0.10)
                )
            bindings.bind(vent.id, "ventilation_opening", product.product_id)
            message = f"Ventilacija {vent.room_id} → {product.name}"
        self.catalog_assignment_status.configure(text=f"DODIJELJENO\n{message}")
        self.status_var.set(f"Proizvod primijenjen: {product.name}")
        self._refresh_catalog_targets()
