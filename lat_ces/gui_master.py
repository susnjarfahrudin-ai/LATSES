"""Master desktop shell over the canonical CompleteBuildingWorkspaceApp."""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk

from lat_ces.building.quantity_takeoff import calculate_quantity_takeoff
from lat_ces.building.reference_house_project import build_reference_house_workflow
from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
from lat_ces.gui_theme import apply_latces_theme
from lat_ces.materials.building_catalog import BuildingMaterialCatalog


class MasterBuildingWorkspaceApp(CompleteBuildingWorkspaceApp):
    """Single desktop workspace using one canonical BuildingModel."""

    def __init__(self) -> None:
        super().__init__()
        apply_latces_theme(self)
        self.catalog = BuildingMaterialCatalog.default()
        self._master_command_panel = None
        self._master_metrics_panel = None
        self._master_metric_vars: dict[str, tk.StringVar] = {}
        self._level_room_text = None
        self._install_master_layout()
        self._install_catalog_tab()
        self._install_window_adaptation()
        self._refresh_master_metrics()
        self._refresh_level_selector()

    def _load_reference_house(self) -> None:
        """Replace the current model with the canonical reference-house workflow."""
        self.workflow = build_reference_house_workflow()
        self.view_step.set(3)
        self.workflow.current_step = 3
        self.workflow.active_level_id = next(iter(self.workflow.model.levels), None)
        self._refresh_complete_tabs()
        self._refresh_master_metrics()
        self._refresh_level_selector()
        self.refresh_view()
        self.status_var.set("Referentna kuća učitana — 3 etaže / canonical BuildingModel")

    def _show_view(self, view: str) -> None:
        """Route master-view commands to the canonical workspace view selector."""
        step_by_view = {"plan": 3, "section": 4, "3d": 5}
        step = step_by_view.get(view)
        if step is None:
            raise ValueError(f"Nepoznat prikaz: {view}")
        self.view_step.set(step)
        self.workflow.current_step = step
        self.goto_step()
        self._refresh_master_metrics()

    def _run_master_validation(self) -> None:
        """Run the canonical BuildingModel validation from the master command panel."""
        self.validate_model()
        self._refresh_master_metrics()

    def _show_engineering_report(self) -> None:
        """Run the canonical engineering report and focus the calculation tab."""
        self._calculate_building_report()
        if hasattr(self, "complete_tabs"):
            tabs = self.complete_tabs.tabs()
            if len(tabs) > 3:
                self.complete_tabs.select(3)

    def _install_window_adaptation(self) -> None:
        self.resizable(True, True)
        self._fullscreen = False
        self._resize_after_id = None
        self.bind("<F11>", lambda _e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda _e: self._exit_fullscreen())
        self.bind("<Control-Key-0>", lambda _e: self._fit_to_screen())
        self.bind("<Configure>", self._on_window_configure, add="+")
        self.after(120, self._fit_to_screen_if_needed)

    def _fit_to_screen_if_needed(self) -> None:
        if self.winfo_screenwidth() < 1450 or self.winfo_screenheight() < 920:
            self._fit_to_screen()

    def _fit_to_screen(self) -> None:
        if self._fullscreen:
            return
        screen_w = max(self.winfo_screenwidth(), 800)
        screen_h = max(self.winfo_screenheight(), 600)
        width = min(1600, screen_w - 24)
        height = min(980, screen_h - 56)
        if sys.platform.startswith("win"):
            try:
                self.state("zoomed")
                return
            except tk.TclError:
                pass
        self.geometry(f"{width}x{height}+{max((screen_w - width)//2, 0)}+{max((screen_h - height)//2, 0)}")

    def _toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        try:
            self.attributes("-fullscreen", self._fullscreen)
        except tk.TclError:
            self._fullscreen = False

    def _exit_fullscreen(self) -> None:
        if not self._fullscreen:
            return
        self._fullscreen = False
        try:
            self.attributes("-fullscreen", False)
        except tk.TclError:
            pass

    def _on_window_configure(self, _event=None) -> None:
        if self._resize_after_id is not None:
            self.after_cancel(self._resize_after_id)
        self._resize_after_id = self.after(120, self._fit_to_screen_if_needed)

    def _install_master_layout(self) -> None:
        self._master_command_panel = ttk.Frame(self, width=220, padding=8)
        self._master_command_panel.pack(side="right", fill="y", padx=(8, 0))
        self._master_command_panel.pack_propagate(False)

        ttk.Label(
            self._master_command_panel,
            text="ALATI",
            style="LATCES.Heading.TLabel",
        ).pack(fill="x", pady=(0, 8))

        for label, command in (
            ("Reference House", self._load_reference_house),
            ("Tlocrt", lambda: self._show_view("plan")),
            ("Presjek", lambda: self._show_view("section")),
            ("3D", lambda: self._show_view("3d")),
            ("Provjera", self._run_master_validation),
            ("Izvještaj", self._show_engineering_report),
        ):
            ttk.Button(self._master_command_panel, text=label, command=command).pack(fill="x", pady=3)

        self._level_room_text = tk.Text(self._master_command_panel, height=18, width=26, wrap="word")
        self._level_room_text.pack(fill="both", expand=True, pady=(12, 0))
        self._level_room_text.configure(state="disabled")

    def _refresh_master_metrics(self) -> None:
        """Refresh optional legacy metrics without requiring the removed panel."""
        if self._master_metrics_panel is None or not self._master_metric_vars:
            self._refresh_level_selector()
            return
        super_refresh = getattr(super(), "_refresh_master_metrics", None)
        if callable(super_refresh):
            super_refresh()

    def _refresh_level_selector(self) -> None:
        if self._level_room_text is None:
            return
        lines: list[str] = []
        for level in self.workflow.model.levels.values():
            lines.append(f"{level.level_id}: {level.name}")
            for room in level.rooms.values():
                lines.append(f"  • {room.name}")
        self._level_room_text.configure(state="normal")
        self._level_room_text.delete("1.0", "end")
        self._level_room_text.insert("1.0", "\n".join(lines) or "Nema etaža/prostorija.")
        self._level_room_text.configure(state="disabled")

    def _install_catalog_tab(self) -> None:
        parent = self.complete_tabs if hasattr(self, "complete_tabs") else self.tabs
        tab = ttk.Frame(parent, padding=8)
        parent.add(tab, text="Materijali")
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill="x", pady=(0, 8))
        self.catalog_search_var = tk.StringVar()
        entry = ttk.Entry(toolbar, textvariable=self.catalog_search_var)
        entry.pack(side="left", fill="x", expand=True)
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
        status = ttk.Label(
            tab,
            text="Parametarski katalog — komercijalne dimenzije i projektne vrijednosti moraju biti verificirane.",
            style="LATCES.Warning.TLabel",
            wraplength=900,
        )
        status.pack(fill="x", pady=(8, 0))
        self._refresh_catalog_view()

    def _refresh_catalog_view(self) -> None:
        query = self.catalog_search_var.get().strip().lower()
        self.catalog_list.delete(0, "end")
        self._catalog_items = []
        for item in self.catalog.search(query):
            self._catalog_items.append(item)
            self.catalog_list.insert("end", f"{item.item_id} — {item.name}")

    def _show_catalog_selection(self, _event=None) -> None:
        selection = self.catalog_list.curselection()
        if not selection:
            return
        item = self._catalog_items[selection[0]]
        lines = [
            f"{item.item_id} — {item.name}",
            f"Jedinica: {item.unit}",
            f"Zahtijeva dimenzije: {'DA' if item.requires_dimensions else 'NE'}",
        ]
        self.catalog_detail.configure(state="normal")
        self.catalog_detail.delete("1.0", "end")
        self.catalog_detail.insert("1.0", "\n".join(lines))
        self.catalog_detail.configure(state="disabled")


def main() -> None:
    app = MasterBuildingWorkspaceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
