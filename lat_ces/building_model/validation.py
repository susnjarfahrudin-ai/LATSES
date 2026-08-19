"""Validation layer used by GUI and CI to report real implementation state."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List
from .core import BuildingModel


class Status(str, Enum):
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    FAIL = "FAIL"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationResult:
    check: str
    status: Status
    message: str


def validate_model(model: BuildingModel) -> List[ValidationResult]:
    results: List[ValidationResult] = []
    if not model.levels:
        return [ValidationResult("levels", Status.FAIL, "building has no levels")]
    results.append(ValidationResult("levels", Status.PASS, f"{len(model.levels)} level(s)"))
    for level in model.levels.values():
        if level.height_m <= 0 or level.length_m <= 0 or level.width_m <= 0:
            results.append(ValidationResult(f"level:{level.id}", Status.FAIL, "invalid level dimensions"))
            continue
        results.append(ValidationResult(f"level:{level.id}", Status.PASS, "dimensions valid"))
        for wall in level.walls.values():
            for opening in wall.openings:
                if opening.z_top_m > wall.height_m:
                    results.append(ValidationResult(f"opening:{wall.id}", Status.FAIL, "opening exceeds wall height"))
                else:
                    results.append(ValidationResult(f"opening:{wall.id}", Status.PASS, "opening is inside wall envelope"))
    return results
