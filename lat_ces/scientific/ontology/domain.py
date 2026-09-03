from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ScientificDomain:
    name: str
    description: str
    def __post_init__(self) -> None:
        if not self.name.strip() or not self.description.strip():
            raise ValueError("ScientificDomain requires name and description")
