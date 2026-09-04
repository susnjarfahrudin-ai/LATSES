from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ScientificDefinition:
    text: str
    reference: str
    version: str
    def __post_init__(self) -> None:
        if not self.text.strip() or not self.reference.strip() or not self.version.strip():
            raise ValueError("ScientificDefinition requires text, reference and version")
