from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceScore:
    evidence_score: float
    method_score: float
    provenance_score: float
    reference_score: float

    def __post_init__(self) -> None:
        for name, value in self.as_components().items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be within [0, 1]")

    def as_components(self) -> dict[str, float]:
        return {
            "evidence_score": self.evidence_score,
            "method_score": self.method_score,
            "provenance_score": self.provenance_score,
            "reference_score": self.reference_score,
        }

    def calculate(self) -> float:
        return sum(self.as_components().values()) / 4.0
