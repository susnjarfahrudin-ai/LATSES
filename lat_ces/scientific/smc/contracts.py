"""Canonical contract for Scientific Models.

This is intentionally domain-neutral; physics and engineering models provide the
actual equations and evidence through references rather than hiding them here.
"""
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class ScientificModelContract:
    model_id: str
    name: str
    version: str
    definition: str
    applicability: str
    assumptions: Sequence[str] = field(default_factory=tuple)
    limitations: Sequence[str] = field(default_factory=tuple)
    inputs: Mapping[str, Any] = field(default_factory=dict)
    outputs: Mapping[str, Any] = field(default_factory=dict)
    units: Mapping[str, str] = field(default_factory=dict)
    dimensions: Mapping[str, str] = field(default_factory=dict)
    provenance_refs: Sequence[str] = field(default_factory=tuple)
    verification_refs: Sequence[str] = field(default_factory=tuple)
    validation_refs: Sequence[str] = field(default_factory=tuple)

    def validate_contract(self) -> None:
        required = (self.model_id, self.name, self.version, self.definition, self.applicability)
        if any(not value for value in required):
            raise ValueError("ScientificModelContract has missing required identity/definition fields")
        if set(self.units) - set(self.inputs) - set(self.outputs):
            raise ValueError("units contain keys that are neither inputs nor outputs")
