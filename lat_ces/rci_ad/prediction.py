"""Deterministic predictive resource calculations."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Prediction:
    horizon: float
    predicted_memory: float
    predicted_resource: float
    resource_feasibility: float

def predict_linear(current: float, rate: float, horizon: float) -> float:
    if horizon < 0: raise ValueError("horizon must be non-negative")
    return max(0.0,current+rate*horizon)

def predict_resource(*, used: float, memory_rate: float, software: float, network: float, storage: float, io: float, total: float, os_reserved: float, reserve: float, horizon: float) -> Prediction:
    predicted_memory=predict_linear(used,memory_rate,horizon)
    denominator=max(1e-12,total-os_reserved-reserve)
    predicted_resource=predicted_memory+software+network+storage+io
    return Prediction(horizon,predicted_memory,predicted_resource,predicted_resource/denominator)
