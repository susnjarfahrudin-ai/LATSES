def update_confidence(old_confidence: float, evidence_factor: float) -> float:
    if not 0.0 <= old_confidence <= 1.0:
        raise ValueError("Old confidence must be within [0, 1]")
    if evidence_factor < 0:
        raise ValueError("Evidence factor cannot be negative")
    return min(1.0, old_confidence + evidence_factor)
