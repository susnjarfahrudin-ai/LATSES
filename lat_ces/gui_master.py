"""Master desktop shell over the canonical CompleteBuildingWorkspaceApp."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from lat_ces.building.quantity_takeoff import calculate_quantity_takeoff
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.gui_theme import apply_latces_theme
from lat_ces.materials.building_catalog import BuildingMaterialCatalog


class MasterBuildingWorkspaceApp(CompleteBuildingWorkspaceApp):
    """Single desktop workspace using one canonical BuildingModel.

    Layout:
    - left: commands/navigation + active BuildingModel selector
    - top: mathematics/engineering metrics
    - center: existing CompleteBuildingWorkspaceApp visualization and tabs
    """

    def __init__(self) -> None:
        super().__init__()
        apply_latces_theme(self)
        self.catalog = BuildingMaterialCatalog.default()
        self._master_command_panel = None
        self._master_metrics_panel = None
        self._master_metric_vars: dict[str, tk.StringVar] = {}
        self._install_master_layout()
        self._install_catalog_tab()
        self._refresh_master_metrics()

    def _install_master_layout(self) -> None:
        self._install_command_panel()
        self._install_metrics_panel()
        if hasattr(self, "complete_tabs"):
            self.complete_tabs.pack_forget()
            self.complete_tabs.pack(fill="x", padx=18, pady=(0, 8), before=self._existing_body())

    def _existing_body(self):
        widgets = list(self.winfo_children())
        for widget in widgets:
            if widget is not self._master_command_panel and widget is not self._master_metrics_panel and widget is not getattr(self, "complete_tabs", None):
                return widget
        return None

    def _install_command_panel(self) -> None:
        panel = ttk.LabelFrame(self, text="Komande", padding=8)
        panel.pack(side="left", fill="y", padx=(10, 8), pady=10)
        self._master_command_panel = panel

        ttk.Label(panel, text="BUILDING MODEL", font=("Segoe UI", 10, "bold")).pack(fill="x", pady=(0, 8))

        ttk.Label(panel, text="Aktivni model").pack(anchor="w")
        self.model_selector_var = tk.StringVar(value=self.workflow.model.name)
        self.model_selector = ttk.Combobox(panel, textvariable=self.model_selector_var, state="readonly", values=(self.workflow.model.name,))
        self.model_selector.pack(fill="x", pady=(2, 10))
        self.model_selector.bind("<<ComboboxSelected>>", self._select_model)

        commands = (
            ("Model", lambda: self._master_goto_step(1)),
            ("Katalog", self._show_catalog_tab),
            ("Tlocrt", lambda: self._master_goto_step(3)),
            ("Presjek", lambda: self._master_goto_step(4)),
            ("3D", lambda: self._master_goto_step(5)),
            ("Konstrukcija", lambda: self._select_complete_tab(2)),
            ("MEP", lambda: self._select_complete_tab(4)),
            ("Provjera", self.validate_model),
            ("Izvještaj", self._calculate_building_report),
        )
        for label, callback in commands:
            ttk.Button(panel, text=label, style="LATCES.Secondary.TButton", command=callback).pack(fill="x", pady=2)

        ttk.Separator(panel).pack(fill="x", pady=8)
        ttk.Button(panel, text="Osvježi matematiku", style="LATCES.Primary.TButton", command=self._refresh_master_metrics).pack(fill="x")

    def _install_metrics_panel(self) -> None:
        panel = ttk.LabelFrame(self, text="Matematika / Engineering", padding=8)
        panel.pack(side="top", fill="x", padx=10, pady=(10, 4))
        self._master_metrics_panel = panel

        metrics = (
            ("area", "Površina"),
            ("volume", "Zapremina"),
            ("wall", "Dužina zidova"),
            ("roof", "Krov — tlocrt"),
            ("levels", "Etaže"),
            ("rooms", "Prostorije"),
            ("elements", "Elementi"),
            ("status", "Status"),
        )
        for index, (key, label) in enumerate(metrics):
            panel.columnconfigure(index, weight=1)
            cell = ttk.Frame(panel)
            cell.grid(row=0, column=index, sticky="ew", padx=3)
            ttk.Label(cell, text=label).pack(anchor="w")
            var = tk.StringVar(value="—")
            self._master_metric_vars[key] = var
            ttk.Label(cell, textvariable=var, font=("Segoe UI", 10, "bold")).pack(anchor="w")

    def _select_model(self, _event=None):
        if self.model_selector_var.get().strip() == self.workflow.model.name:
            self._refresh_master_metrics()

    def _master_goto_step(self, step: int) -> None:
        self.view_step.set(step)
        self.goto_step()
        self._refresh_master_metrics()

    def _select_complete_tab(self, index: int) -> None:
        if hasattr(self, "complete_tabs") and index < len(self.complete_tabs.tabs()):
            self.complete_tabs.select(index)
            self._refresh_master_metrics()

    def _show_catalog_tab(self) -> None:
        if hasattr(self, "complete_tabs") and self.complete_tabs.tabs():
            self.complete_tabs.select(self.complete_tabs.tabs()[-1])

    def _refresh_master_metrics(self) -> None:
        model = self.workflow.model
        qto = calculate_quantity_takeoff(model)
        self._master_metric_vars["area"].set(f"{qto.floor_area_m2:.2f} m²")
        self._master_metric_vars["volume"].set(f"{qto.volume_m3:.2f} m³")
        self._master_metric_vars["wall"].set(f"{qto.wall_length_m:.2f} m")
        self._master_metric_vars["roof"].set(f"{qto.roof_plan_area_m2:.2f} m²")
        self._master_metric_vars["levels"].set(str(len(model.levels)))
        self._master_metric_vars["rooms"].set(str(model.room_count))
        self._master_metric_vars["elements"].set(str(model.element_count))
        findings = model.validate()
        self._master_metric_vars["status"].set("PASS" if not findings else f"CHECK ({len(findings)})")

    def refresh_view(self):
        super().refresh_view()
        if hasattr(self, "_master_metric_vars"):
            self._refresh_master_metrics()

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


def main() -> None:
    MasterBuildingWorkspaceApp().mainloop()


if __name__ == "__main__":
    main()
