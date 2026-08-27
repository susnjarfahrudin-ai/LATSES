from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class ScientificMethod:
    method_id: str
    procedure: str
    parameters: Mapping[str, Any]
    limitations: str

    def __post_init__(self) -> None:
        if not self.method_id.strip():
            raise ValueError("Method ID is required")
        if not self.procedure.strip():
            raise ValueError("Method procedure is required")
        if not self.limitations.strip():
            raise ValueError("Method limitations are required")
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
