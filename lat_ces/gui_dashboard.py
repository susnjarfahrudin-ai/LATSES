"""Project overview entrypoint layered on the canonical LAT-CES GUI.

The dashboard is a navigation/summary layer only. It never creates a second
BuildingModel; the product catalog is a shared selection/data layer.
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building.model import Material
from lat_ces.building_model.quantities import to_quantity_view
from lat_ces.catalog.product_catalog import all_products, categories, products_for_category
from lat_ces.gui_launcher import CompleteBuildingWorkspaceApp


class ProjectOverviewApp(CompleteBuildingWorkspaceApp):
    """Canonical GUI with a first-class project overview/dashboard."""

    def __init__(self) -> None:
        super().__init__()
        self._repair_visual_workspace_layout()
        self._install_project_overview()
        self._install_catalog_tab()
        self._refresh_project_overview()
        self._select_overview_tab()

    def _repair_visual_workspace_layout(self) -> None:
        """Keep the main visual workspace large and above the control notebook."""
        canvas_parent = self.canvas
        while canvas_parent.master is not self:
            canvas_parent = canvas_parent.master
        body = canvas_parent
        notebook = getattr(self, "complete_tabs", None)
        if body is None or notebook is None:
            return

        body.pack_forget()
        body.pack(fill="both", expand=True, padx=18, pady=(0, 8))
        notebook.pack_forget()
        notebook.pack(fill="x", padx=18, pady=(0, 8))
        self.update_idletasks()

    def _select_overview_tab(self) -> None:
        for index in range(self.complete_tabs.index("end")):
            if self.complete_tabs.tab(index, "text") == "Pregled projekta":
                self.complete_tabs.select(index)
                return

    def _select_tab(self, title: str) -> None:
        for index in range(self.complete_tabs.index("end")):
            if self.complete_tabs.tab(index, "text") == title:
                self.complete_tabs.select(index)
                self.status_var.set(f"Otvoren prikaz: {title}")
                return

    def _install_project_overview(self) -> None:
        frame = ttk.Frame(self.complete_tabs, padding=14)
        self.complete_tabs.insert(0, frame, text="Pregled projekta")
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Label(header, text="LAT-CES", font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Label(header, text="  Engineering Workspace", font=("Segoe UI", 11)).pack(side="left", pady=(6, 0))
        ttk.Button(header, text="Osvježi pregled", command=self._refresh_project_overview).pack(side="right")

        left = ttk.LabelFrame(frame, text="Radni tok", padding=12)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)

        steps = (
            ("1", "Reference House", "Model / Pogledi"),
            ("2", "Tlocrt", "Model / Pogledi"),
            ("3", "Presjek", "Model / Pogledi"),
            ("4", "3D", "Model / Pogledi"),
            ("5", "Provjera", "Proračuni"),
            ("6", "Izvještaj", "Engineering Summary"),
            ("7", "Katalog proizvoda", "Katalog proizvoda"),
            ("8", "Materijali", "Konstrukcija / Statika"),
            ("9", "MEP", "MEP"),
        )
        for row, (number, label, tab_name) in enumerate(steps):
            card = ttk.Frame(left, padding=5)
            card.grid(row=row, column=0, sticky="ew", pady=3)
            ttk.Label(card, text=number, width=3, font=("Segoe UI", 11, "bold")).pack(side="left")
            ttk.Label(card, text=label, font=("Segoe UI", 10, "bold")).pack(side="left", padx=(6, 10))
            ttk.Button(card, text="Otvori", command=lambda title=tab_name: self._select_tab(title)).pack(side="right")

        hint = ttk.Label(left, text="Svi prikazi čitaju isti canonical BuildingModel. Katalog je zajednički Product/Material sloj, ne drugi model.", wraplength=620)
        hint.grid(row=len(steps), column=0, sticky="w", pady=(10, 0))

        right = ttk.LabelFrame(frame, text="Trenutni model", padding=12)
        right.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        right.rowconfigure(2, weight=1)
        self.overview_identity = ttk.Label(right, font=("Segoe UI", 11, "bold"), wraplength=360)
        self.overview_identity.grid(row=0, column=0, sticky="w")
        self.overview_model = ttk.Label(right, wraplength=360)
        self.overview_model.grid(row=1, column=0, sticky="w", pady=(8, 10))
        self.overview_stats = tk.Text(right, height=18, width=46, wrap="word")
        self.overview_stats.grid(row=2, column=0, sticky="nsew")
        self.overview_stats.configure(state="disabled")

        footer = ttk.Frame(frame)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ttk.Button(footer, text="Otvori tlocrt", command=lambda: self._select_tab("Model / Pogledi")).pack(side="left")
        ttk.Button(footer, text="Katalog", command=lambda: self._select_tab("Katalog proizvoda")).pack(side="left", padx=6)
        ttk.Button(footer, text="Provjeri model", command=self.validate_model).pack(side="left", padx=6)
        ttk.Button(footer, text="Model Inspector", command=self.show_canonical_model_inspector).pack(side="left")

    def _install_catalog_tab(self) -> None:
        frame = ttk.Frame(self.complete_tabs, padding=12)
        self.complete_tabs.add(frame, text="Katalog proizvoda")
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        ttk.Label(header, text="Katalog proizvoda i materijala", font=("Segoe UI", 13, "bold")).pack(side="left")
        ttk.Label(header, text="  Verified / Reference / Missing", foreground="#475569").pack(side="left", padx=8)

        self.catalog_category_var = tk.StringVar(value=categories()[0])
        ttk.Label(header, text="Kategorija:").pack(side="right")
        category_combo = ttk.Combobox(header, textvariable=self.catalog_category_var, state="readonly", values=categories(), width=24)
        category_combo.pack(side="right", padx=(6, 12))
        category_combo.bind("<<ComboboxSelected>>", lambda _event: self._refresh_catalog_products())

        left = ttk.Frame(frame)
        left.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        columns = ("name", "manufacturer", "dimensions", "status")
        self.catalog_tree = ttk.Treeview(left, columns=columns, show="headings", selectmode="browse")
        headings = {"name": "Proizvod", "manufacturer": "Proizvođač", "dimensions": "Dimenzije", "status": "Podaci"}
        widths = {"name": 280, "manufacturer": 150, "dimensions": 150, "status": 110}
        for column in columns:
            self.catalog_tree.heading(column, text=headings[column])
            self.catalog_tree.column(column, width=widths[column], anchor="w")
        self.catalog_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.catalog_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.catalog_tree.configure(yscrollcommand=scrollbar.set)
        self.catalog_tree.bind("<<TreeviewSelect>>", lambda _event: self._show_selected_product())

        right = ttk.LabelFrame(frame, text="Odabrani proizvod", padding=12)
        right.grid(row=1, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        self.catalog_detail_title = ttk.Label(right, font=("Segoe UI", 12, "bold"), wraplength=360)
        self.catalog_detail_title.grid(row=0, column=0, sticky="w")
        self.catalog_detail = tk.Text(right, height=16, width=44, wrap="word")
        self.catalog_detail.grid(row=1, column=0, sticky="nsew", pady=(8, 8))
        self.catalog_detail.configure(state="disabled")
        self.catalog_add_button = ttk.Button(right, text="Dodaj u BuildingModel materijale", command=self._add_selected_catalog_material)
        self.catalog_add_button.grid(row=2, column=0, sticky="ew")
        ttk.Label(
            right,
            text="Nedostajući podaci ostaju N/A. Katalog ih ne izmišlja; kasnije se mogu popuniti iz proizvođačkog izvora, bSDD ili EPD adaptera.",
            wraplength=360,
            foreground="#92400e",
        ).grid(row=3, column=0, sticky="w", pady=(8, 0))
        self._refresh_catalog_products()

    def _refresh_catalog_products(self) -> None:
        if not hasattr(self, "catalog_tree"):
            return
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)
        for product in products_for_category(self.catalog_category_var.get()):
            self.catalog_tree.insert(
                "",
                "end",
                iid=product.product_id,
                values=(product.name, product.manufacturer or "—", product.dimensions or "—", product.status),
            )
        items = self.catalog_tree.get_children()
        if items:
            self.catalog_tree.selection_set(items[0])
            self.catalog_tree.focus(items[0])
            self._show_selected_product()

    def _selected_catalog_product(self):
        selection = self.catalog_tree.selection() if hasattr(self, "catalog_tree") else ()
        if not selection:
            return None
        product_id = selection[0]
        return next((product for product in all_products() if product.product_id == product_id), None)

    def _show_selected_product(self) -> None:
        product = self._selected_catalog_product()
        if product is None:
            return
        self.catalog_detail_title.configure(text=product.engineering_summary)
        values = [
            f"Kategorija: {product.category}",
            f"Proizvođač: {product.manufacturer or 'Nije naveden'}",
            f"Dimenzije: {product.dimensions or 'Nije navedeno'}",
            f"Status podataka: {product.status}",
            f"Gustina: {product.density_kg_m3 if product.density_kg_m3 is not None else 'N/A'} kg/m³",
            f"E: {product.youngs_modulus_pa if product.youngs_modulus_pa is not None else 'N/A'} Pa",
            f"λ: {product.thermal_conductivity_w_mk if product.thermal_conductivity_w_mk is not None else 'N/A'} W/mK",
            f"Čvrstoća: {product.compressive_strength_mpa if product.compressive_strength_mpa is not None else 'N/A'} MPa",
            f"Izvor: {product.source or 'Nije naveden'}",
        ]
        self.catalog_detail.configure(state="normal")
        self.catalog_detail.delete("1.0", "end")
        self.catalog_detail.insert("1.0", "\n".join(values))
        self.catalog_detail.configure(state="disabled")
        material_categories = {"Zidovi", "Beton", "Izolacija"}
        self.catalog_add_button.configure(state="normal" if product.category in material_categories else "disabled")

    def _add_selected_catalog_material(self) -> None:
        product = self._selected_catalog_product()
        if product is None or product.category not in {"Zidovi", "Beton", "Izolacija"}:
            return
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
        existing = next((item for item in self.workflow.model.materials.values() if item.product_id == product.product_id), None)
        if existing is None:
            self.workflow.model.add_material(material)
            self.status_var.set(f"Katalog: dodat materijal {product.name}")
        else:
            self.status_var.set(f"Katalog: materijal već postoji — {product.name}")
        self._refresh_complete_tabs()
        self._refresh_project_overview()

    def _refresh_project_overview(self) -> None:
        if not hasattr(self, "overview_identity"):
            return
        model = self.workflow.model
        q = to_quantity_view(model)
        registry = ensure_mep_registry(model)
        self.overview_identity.configure(text=f"{model.name} · {len(model.levels)} etaže")
        self.overview_model.configure(
            text=(
                f"Aktivna etaža: {self.active_level.name}\n"
                f"Gabarit: {self.active_level.length_m:.2f} × {self.active_level.width_m:.2f} m\n"
                f"Visina etaže: {self.active_level.height:.2f} m"
            )
        )
        lines = [
            "OBJEKTI",
            f"Prostorije: {len(q.rooms)}",
            f"Zidovi: {len(q.walls)}",
            f"Otvori: {len(q.openings)}",
            f"Stepeništa: {len(q.stairs)}",
            f"Terase: {len(q.terraces)}",
            f"Materijali/Proizvodi: {len(model.materials)}",
            "",
            "KOLIČINE",
            f"Površina prostorija: {sum(r.floor_area_m2 for r in q.rooms):.2f} m²",
            f"Volumen prostorija: {sum(r.volume_m3 for r in q.rooms):.2f} m³",
            "",
            "MEP",
            f"Ventilacija: {len(registry.all_ventilation_openings)}",
            f"Voda: {len(registry.all_water_branches)}",
            f"Grijanje: {len(registry.all_heating_zones)}",
            "",
            "INTEGRITET",
            "Jedan BuildingModel = source of truth",
        ]
        self.overview_stats.configure(state="normal")
        self.overview_stats.delete("1.0", "end")
        self.overview_stats.insert("1.0", "\n".join(lines))
        self.overview_stats.configure(state="disabled")


def run_dashboard_acceptance() -> None:
    """Deterministic packaged-EXE smoke for the overview dashboard."""
    app = ProjectOverviewApp()
    try:
        app.update_idletasks()
        tabs = [app.complete_tabs.tab(i, "text") for i in range(app.complete_tabs.index("end"))]
        assert tabs[0] == "Pregled projekta", f"Dashboard not first tab: {tabs}"
        assert "Katalog proizvoda" in tabs
        assert app.workflow.model.levels, "Reference House is not loaded"
        assert "Model / Pogledi" in tabs
        assert "Proračuni" in tabs
        assert "Konstrukcija / Statika" in tabs
        assert "MEP" in tabs
        catalog_items = sum(len(products_for_category(category)) for category in categories())
        assert catalog_items >= 10, f"Catalog too small: {catalog_items}"
        canvas_top = app.canvas.winfo_rooty()
        controls_top = app.complete_tabs.winfo_rooty()
        assert canvas_top < controls_top, "Visual workspace must be above engineering controls"
        assert app.canvas.winfo_height() >= 250, f"Visual workspace too small: {app.canvas.winfo_height()} px"
        for step, title in ((3, "Tlocrt"), (4, "Presjek"), (5, "3D")):
            app.view_step.set(step)
            app.goto_step()
            app.update_idletasks()
            if not app.canvas.find_all():
                raise RuntimeError(f"{title}: canvas has no rendered content")
        findings = app.workflow.validate()
        if findings:
            raise RuntimeError("Provjera: " + "; ".join(findings))
        app._select_tab("Engineering Summary")
        app.refresh_engineering_summary()
        summary = app.engineering_summary.get("1.0", "end")
        for marker in ("STATIKA", "TERMIKA", "KOLIČINE", "MEP"):
            assert marker in summary, f"Engineering Summary missing {marker}"
        assert app.workflow.model.materials, "Material registry is empty"
        print("GUI DASHBOARD GREEN: overview + catalog + Reference House + Tlocrt + Presjek + 3D + Provjera + Izvještaj + Materijali + MEP")
        print("GUI DASHBOARD GREEN: overview + large visual workspace + Reference House + Tlocrt + Presjek + 3D + Provjera + Izvještaj + Materijali + MEP")
    finally:
        app.destroy()


def main() -> None:
    if os.environ.get("LATCES_GUI_ACCEPTANCE") == "1":
        run_dashboard_acceptance()
        return
    ProjectOverviewApp().mainloop()


if __name__ == "__main__":
    main()
