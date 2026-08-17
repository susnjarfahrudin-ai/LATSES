"""Deterministic in-memory registry for SMC-controlled scientific models."""
from .contracts import ScientificModelContract

class SMCRegistry:
    def __init__(self):
        self._models = {}

    def register(self, model: ScientificModelContract) -> None:
        model.validate_contract()
        key = (model.model_id, model.version)
        if key in self._models:
            raise ValueError(f"model already registered: {key}")
        self._models[key] = model

    def get(self, model_id: str, version: str) -> ScientificModelContract:
        return self._models[(model_id, version)]

    def ids(self):
        return tuple(sorted(self._models))
