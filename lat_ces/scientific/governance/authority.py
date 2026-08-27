from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Authority:
    identity: str
    level: int
    scope: str

    def __post_init__(self) -> None:
        if not self.identity.strip() or not self.scope.strip() or self.level not in {0, 1, 2, 3}:
            raise ValueError("Authority requires identity, scope and level 0-3")
