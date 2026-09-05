"""Platform-neutral host telemetry for the RCI-AD observation boundary.

This module observes only. It does not make security decisions, throttle work,
or modify the existing limiter.
"""

from __future__ import annotations

import os
import platform
import time
from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class HostTelemetry:
    timestamp: float
    platform: str
    cpu_model: Optional[str]
    logical_cpu: Optional[int]
    physical_cpu: Optional[int]
    cpu_percent: Optional[float]
    load_1m: Optional[float]
    ram_total_bytes: Optional[int]
    ram_available_bytes: Optional[int]
    ram_used_bytes: Optional[int]
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _linux_cpu_model() -> Optional[str]:
    try:
        with open("/proc/cpuinfo", encoding="utf-8") as fh:
            for line in fh:
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
    except (OSError, UnicodeError):
        return None
    return None


def _linux_memory() -> tuple[Optional[int], Optional[int]]:
    try:
        values: dict[str, int] = {}
        with open("/proc/meminfo", encoding="utf-8") as fh:
            for line in fh:
                key, value = line.split(":", 1)
                parts = value.split()
                if parts:
                    values[key] = int(parts[0]) * 1024
        total = values.get("MemTotal")
        available = values.get("MemAvailable")
        return total, available
    except (OSError, ValueError, UnicodeError):
        return None, None


def _linux_cpu_times() -> Optional[tuple[int, int]]:
    try:
        with open("/proc/stat", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("cpu "):
                    fields = [int(x) for x in line.split()[1:]]
                    idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
                    total = sum(fields)
                    return total, idle
    except (OSError, ValueError, UnicodeError):
        return None
    return None


def _cpu_percent_linux(interval: float) -> Optional[float]:
    before = _linux_cpu_times()
    if before is None:
        return None
    time.sleep(max(0.0, interval))
    after = _linux_cpu_times()
    if after is None:
        return None
    total_delta = after[0] - before[0]
    idle_delta = after[1] - before[1]
    if total_delta <= 0:
        return None
    return round(100.0 * (1.0 - idle_delta / total_delta), 2)


def _windows_memory() -> tuple[Optional[int], Optional[int]]:
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return int(status.ullTotalPhys), int(status.ullAvailPhys)
    except (AttributeError, OSError, TypeError):
        pass
    return None, None


def _windows_cpu_percent(interval: float) -> Optional[float]:
    try:
        import ctypes

        class FILETIME(ctypes.Structure):
            _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]

        def read_times() -> tuple[int, int, int]:
            idle, kernel, user = FILETIME(), FILETIME(), FILETIME()
            ok = ctypes.windll.kernel32.GetSystemTimes(
                ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)
            )
            if not ok:
                raise OSError("GetSystemTimes failed")
            def value(ft: FILETIME) -> int:
                return (ft.dwHighDateTime << 32) | ft.dwLowDateTime
            return value(idle), value(kernel), value(user)

        before = read_times()
        time.sleep(max(0.0, interval))
        after = read_times()
        total = (after[1] + after[2]) - (before[1] + before[2])
        idle = after[0] - before[0]
        if total <= 0:
            return None
        return round(100.0 * (1.0 - idle / total), 2)
    except (AttributeError, OSError, TypeError):
        return None


def collect_host_telemetry(interval: float = 0.05) -> HostTelemetry:
    """Collect one host snapshot; unavailable metrics are returned as ``None``."""
    system = platform.system()
    logical = os.cpu_count()
    model: Optional[str] = None
    physical: Optional[int] = None
    total: Optional[int] = None
    available: Optional[int] = None
    cpu_percent: Optional[float] = None
    load_1m: Optional[float] = None
    sources: list[str] = []

    if system == "Linux":
        model = _linux_cpu_model()
        times = _linux_cpu_times()
        if times is not None:
            sources.append("/proc/stat")
        total, available = _linux_memory()
        if total is not None:
            sources.append("/proc/meminfo")
        cpu_percent = _cpu_percent_linux(interval)
        try:
            load_1m = os.getloadavg()[0]
        except (AttributeError, OSError):
            load_1m = None
        # /proc/cpuinfo exposes logical processors reliably; physical topology
        # is optional and deliberately remains unavailable if not explicit.
        physical = None
        if model is not None:
            sources.append("/proc/cpuinfo")
    elif system == "Windows":
        total, available = _windows_memory()
        cpu_percent = _windows_cpu_percent(interval)
        sources.extend(["GlobalMemoryStatusEx", "GetSystemTimes"])
        model = platform.processor() or None
        physical = None
        load_1m = None
    else:
        model = platform.processor() or None
        try:
            load_1m = os.getloadavg()[0]
        except (AttributeError, OSError):
            load_1m = None
        sources.append("stdlib")

    used = total - available if total is not None and available is not None else None
    return HostTelemetry(
        timestamp=time.time(),
        platform=system,
        cpu_model=model,
        logical_cpu=logical,
        physical_cpu=physical,
        cpu_percent=cpu_percent,
        load_1m=load_1m,
        ram_total_bytes=total,
        ram_available_bytes=available,
        ram_used_bytes=used,
        source=",".join(sources),
    )
