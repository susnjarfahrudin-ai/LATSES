"""Universal I/O and data-carrier contracts."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class Direction(str, Enum):
    IN="IN"; OUT="OUT"; BIDIRECTIONAL="BIDIRECTIONAL"; CONTROL="CONTROL"

@dataclass(frozen=True)
class InterfaceObservation:
    interface_id: str
    device_id: Optional[str]
    interface_type: str
    protocol: Optional[str]
    direction: Direction
    capacity: Optional[float]
    current_rate: Optional[float]
    queue_depth: Optional[float]
    buffer_size: Optional[float]
    dma_usage: Optional[float]
    driver_id: Optional[str]
    controller_id: Optional[str]
    source_id: Optional[str]
    destination_id: Optional[str]
    integrity_state: str
    trust_state: str
    timestamp: float
    confidence: float

@dataclass(frozen=True)
class DataCarrier:
    source_id: str
    device_id: Optional[str]
    interface_id: str
    data_type: str
    direction: Direction
    protocol: Optional[str]
    size: float
    rate: float
    concurrency: float
    queue_depth: float
    buffer_usage: float
    dma_usage: float
    cpu_cost: float
    memory_cost: float
    latency: float
    timestamp: float
    integrity_state: str
    trust_state: str
    confidence: float

    def __post_init__(self) -> None:
        for name in ("size","rate","concurrency","queue_depth","buffer_usage","dma_usage","cpu_cost","memory_cost","latency"):
            value=getattr(self,name)
            if value < 0: raise ValueError(f"{name} must be non-negative")
        if not 0 <= self.confidence <= 1: raise ValueError("confidence must be between 0 and 1")
        if not self.source_id or not self.interface_id or not self.data_type: raise ValueError("source_id, interface_id and data_type are required")

IO_CATEGORIES=("NETWORK","LOCAL_IPC","STORAGE","REMOVABLE_STORAGE","WIRELESS","WIRED","OPTICAL","PERIPHERAL","BUS","DISPLAY","AUDIO","SERIAL","OTHER_IO")
DEFAULT_INTERFACE_TYPES=("USB","USB-C","Thunderbolt","Ethernet","Wi-Fi","Bluetooth","NFC","PCI","PCIe","SATA","NVMe","SD","microSD","FireWire","Serial","UART","RS-232","RS-485","Optical","HDMI","DisplayPort","Audio","Camera","Docking interface","Other I/O")
