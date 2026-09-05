from __future__ import annotations

def calculate_confidence(confidence_values: tuple[float, ...]) -> float:
    if not confidence_values:
        return 0.0
    if any(not 0.0 <= value <= 1.0 for value in confidence_values):
        raise ValueError("Confidence values must be within [0, 1]")
    return min(confidence_values)
