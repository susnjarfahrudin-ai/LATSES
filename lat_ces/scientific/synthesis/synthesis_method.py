from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class SynthesisMethod:
    method_id: str
    name: str
    domain: str
    description: str
    constraints: tuple[str, ...] = ()
