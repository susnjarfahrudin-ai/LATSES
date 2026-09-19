"""Host-wide resource and communication pressure model."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .universal_io import DataCarrier, InterfaceObservation

@dataclass(frozen=True)
class ResourceState:
    ram: float; cpu: float; disk: float; network: float; io: float; module: float; attack: float

@dataclass(frozen=True)
class PressureResult:
    resource: ResourceState
    packet_weight: float
    total_pressure: float
    resource_feasibility: float
    confidence: float

def _clamp(x: float) -> float: return max(0.0,min(1.0,float(x)))

def data_unit_weight(data: DataCarrier, *, weights=(.20,.15,.15,.20,.15,.10,.05)) -> float:
    values=(_clamp(data.size/1_000_000),_clamp(data.rate/1_000_000),_clamp(data.concurrency/100),_clamp(data.memory_cost/1_000_000),_clamp(1.0/max(1.0,data.latency)),_clamp(data.cpu_cost),_clamp(data.dma_usage/100))
    return sum(w*v for w,v in zip(weights,values))

def interface_pressure(obs: InterfaceObservation) -> float:
    vals=[obs.current_rate or 0.0,obs.queue_depth or 0.0,obs.buffer_size or 0.0,obs.dma_usage or 0.0]
    normalized=[_clamp(v/1_000_000) if i==0 else _clamp(v/100) for i,v in enumerate(vals)]
    return sum(normalized)/len(normalized)

def host_pressure(*, ram: float, cpu: float, disk: float, network: float, io: float, attack: float, module: float=0.0, weights=(.20,.15,.15,.20,.15,.15)) -> ResourceState:
    return ResourceState(*[_clamp(v) for v in (ram,cpu,disk,network,io,module,attack)])

def pressure_model(state: ResourceState, packet_weight: float, resource_feasibility: float, confidence: float, *, weights=(.20,.15,.15,.20,.15,.15)) -> PressureResult:
    total=sum(w*v for w,v in zip(weights,(state.ram,state.cpu,state.disk,state.network,state.io,state.attack)))
    return PressureResult(state,packet_weight,total,resource_feasibility,confidence)

def safe_ram_budget(total: float, os_used: float, expected_software: float, reserve: float) -> float:
    return max(0.0,total-os_used-expected_software-reserve)

def resource_feasibility(*, predicted_software: float, predicted_network: float, predicted_storage: float, predicted_io: float, total: float, os_reserved: float, reserve: float) -> float:
    denominator=max(1e-12,total-os_reserved-reserve)
    return (predicted_software+predicted_network+predicted_storage+predicted_io)/denominator
