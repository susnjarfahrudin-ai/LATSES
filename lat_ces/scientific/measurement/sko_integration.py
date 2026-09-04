from __future__ import annotations

from typing import Any

from lat_ces.core.sko import ScientificKnowledgeObject


def measurement_to_sko(measurement, *, title: str | None = None) -> ScientificKnowledgeObject:
    """Represent a measurement as a canonical SKO evidence record."""
    payload = measurement.to_record()
    payload["object_type"] = "Measurement"
    payload["definition"] = "Traceable observation of a physical quantity."
    payload["created_by"] = "LAT-CES Measurement Engine"
    return ScientificKnowledgeObject(
        sko_id=f"SKO-{measurement.measurement_id}",
        title=title or f"Measurement {measurement.measurement_id}",
        payload=payload,
    )


def hardened_measurement_to_sko(hardened_measurement, *, title: str | None = None) -> ScientificKnowledgeObject:
    """Represent the complete hardened measurement chain as an SKO record."""
    measurement = hardened_measurement.measurement
    payload: dict[str, Any] = measurement.to_record()
    payload.update(
        {
            "object_type": "HardenedMeasurement",
            "definition": "Integrity-protected and traceable measurement record.",
            "integrity_hash": hardened_measurement.integrity_hash,
            "revision": hardened_measurement.revision,
            "audit": hardened_measurement.audit.__dict__,
            "evidence": hardened_measurement.evidence.to_record(),
            "created_by": "LAT-CES Measurement Engine",
        }
    )
    return ScientificKnowledgeObject(
        sko_id=f"SKO-{measurement.measurement_id}",
        title=title or f"Hardened Measurement {measurement.measurement_id}",
        payload=payload,
    )


__all__ = ["measurement_to_sko", "hardened_measurement_to_sko"]
