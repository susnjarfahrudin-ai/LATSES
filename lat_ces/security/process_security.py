"""Process identity and platform hardening primitives."""
from __future__ import annotations

import ctypes
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal


@dataclass(frozen=True)
class ProcessIdentity:
    pid: int
    process_uuid: str
    created_at_utc: str
    kernel_start_token: str

    @property
    def fingerprint(self) -> str:
        return f"{self.pid}:{self.kernel_start_token}"


@dataclass(frozen=True)
class ProcessIsolationResult:
    platform: Literal["linux", "windows", "other"]
    dump_protection: bool
    dynamic_code_mitigation: bool
    extension_point_mitigation: bool


def _linux_start_token(pid: int) -> str:
    with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as handle:
        raw = handle.read()
    remainder = raw.rsplit(") ", 1)[1]
    fields = remainder.split()
    if len(fields) <= 19:
        raise RuntimeError("/proc process stat record is incomplete")
    return fields[19]  # field 22 overall: process starttime in clock ticks


def _windows_start_token(pid: int) -> str:
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel32.OpenProcess.restype = ctypes.c_void_p
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0, pid)
    if not handle:
        raise OSError(ctypes.get_last_error(), "OpenProcess failed")

    class FILETIME(ctypes.Structure):
        _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]

    creation = FILETIME()
    exit_time = FILETIME()
    kernel_time = FILETIME()
    user_time = FILETIME()
    try:
        ok = kernel32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exit_time),
            ctypes.byref(kernel_time),
            ctypes.byref(user_time),
        )
        if not ok:
            raise OSError(ctypes.get_last_error(), "GetProcessTimes failed")
        value = (creation.dwHighDateTime << 32) | creation.dwLowDateTime
        return str(value)
    finally:
        kernel32.CloseHandle(handle)


def process_start_token(pid: int) -> str:
    if pid <= 0:
        raise ValueError("pid must be positive")
    if sys.platform.startswith("linux"):
        return _linux_start_token(pid)
    if sys.platform == "win32":
        return _windows_start_token(pid)
    raise RuntimeError(f"process start token unsupported on {sys.platform}")


def current_process_identity() -> ProcessIdentity:
    pid = os.getpid()
    return ProcessIdentity(
        pid=pid,
        process_uuid=str(uuid.uuid4()),
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        kernel_start_token=process_start_token(pid),
    )


def is_process_alive(pid: int, expected_fingerprint: str) -> bool:
    if not expected_fingerprint:
        return False
    try:
        return f"{pid}:{process_start_token(pid)}" == expected_fingerprint
    except (FileNotFoundError, OSError, RuntimeError, ValueError):
        return False


def activate_process_isolation(*, strict: bool = False) -> ProcessIsolationResult:
    """Apply native process hardening available on the current platform.

    Linux disables the dumpable flag, which also blocks normal ptrace attach.
    Windows uses supported process-mitigation policies that reduce dynamic-code
    and extension-point injection. Neither platform claim is equivalent to
    protection from a privileged kernel attacker.
    """
    if sys.platform.startswith("linux"):
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        result = libc.prctl(13, 0, 0, 0, 0)  # PR_SET_DUMPABLE = 13
        if result != 0:
            error = ctypes.get_errno()
            if strict:
                raise OSError(error, "PR_SET_DUMPABLE failed")
            return ProcessIsolationResult("linux", False, False, False)
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except (ImportError, OSError, ValueError):
            pass
        return ProcessIsolationResult("linux", True, False, False)

    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.SetProcessMitigationPolicy.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t]
        kernel32.SetProcessMitigationPolicy.restype = ctypes.c_int
        dynamic_code = ctypes.c_uint32(1)       # ProhibitDynamicCode
        extension_points = ctypes.c_uint32(1)   # DisableExtensionPoints
        dynamic_ok = bool(kernel32.SetProcessMitigationPolicy(2, ctypes.byref(dynamic_code), ctypes.sizeof(dynamic_code)))
        extension_ok = bool(kernel32.SetProcessMitigationPolicy(7, ctypes.byref(extension_points), ctypes.sizeof(extension_points)))
        if strict and not (dynamic_ok and extension_ok):
            raise OSError(ctypes.get_last_error(), "Windows process mitigation could not be applied")
        return ProcessIsolationResult("windows", False, dynamic_ok, extension_ok)

    if strict:
        raise RuntimeError(f"process isolation unsupported on {sys.platform}")
    return ProcessIsolationResult("other", False, False, False)


__all__ = ["ProcessIdentity", "ProcessIsolationResult", "activate_process_isolation", "current_process_identity", "is_process_alive", "process_start_token"]
