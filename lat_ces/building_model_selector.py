"""Reusable selector for canonical BuildingModel instances."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping

import tkinter as tk
from tkinter import ttk

from lat_ces.building.model import BuildingModel


@dataclass(frozen=True)
class BuildingModelOption:
    key: str
    label: str
    model: BuildingModel


class BuildingModelSelector(ttk.LabelFrame):
    """Select an already-constructed canonical BuildingModel instance."""

    def __init__(
        self,
        master: tk.Misc,
        models: Mapping[str, BuildingModel],
        *,
        on_selected: Callable[[BuildingModel], None] | None = None,
        title: str = "BuildingModel selector",
    ) -> None:
        super().__init__(master, text=title, padding=8)
        self._models = dict(models)
        self._on_selected = on_selected or (lambda _model: None)
        self.variable = tk.StringVar(master=self)
        values = list(self._models)
        self.combo = ttk.Combobox(self, textvariable=self.variable, values=values, state="readonly")
        self.combo.pack(fill="x")
        self.combo.bind("<<ComboboxSelected>>", self._selection_changed)
        if values:
            self.variable.set(values[0])

    def _selection_changed(self, _event: tk.Event) -> None:
        key = self.variable.get()
        model = self._models.get(key)
        if model is not None:
            self._on_selected(model)

    @property
    def selected_model(self) -> BuildingModel | None:
        return self._models.get(self.variable.get())

    def set_models(self, models: Mapping[str, BuildingModel]) -> None:
        self._models = dict(models)
        self.combo["values"] = list(self._models)
        if self._models:
            self.variable.set(next(iter(self._models)))
        else:
            self.variable.set("")


__all__ = ["BuildingModelOption", "BuildingModelSelector"]
