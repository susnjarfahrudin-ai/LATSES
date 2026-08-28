from __future__ import annotations

from .measurement import Measurement


class MeasurementRegistry:
    """Deterministic registry for canonical measurements."""

    def __init__(self) -> None:
        self._items: dict[str, Measurement] = {}

    def register(self, measurement: Measurement) -> Measurement:
        measurement.validate()
        existing = self._items.get(measurement.measurement_id)
        if existing is not None and existing != measurement:
            raise ValueError(f"Measurement identity collision: {measurement.measurement_id}")
        self._items[measurement.measurement_id] = measurement
        return measurement

    def get(self, measurement_id: str) -> Measurement | None:
        return self._items.get(measurement_id)

    def all(self) -> tuple[Measurement, ...]:
        return tuple(self._items.values())

    def __len__(self) -> int:
        return len(self._items)

    def __contains__(self, measurement_id: str) -> bool:
        return measurement_id in self._items


__all__ = ["MeasurementRegistry"]
