"""Read-only runtime instrumentation for security load experiments.

This test module measures the host/process envelope around the existing
adversarial experiment. It does not alter production security logic, limiter
parameters, baselines, payloads, or decision rules.
"""
from __future__ import annotations

import json
import os
import platform
try:
    import resource
except ImportError:  # Windows and other platforms without POSIX resource
    resource = None
import threading
import time
from collections import Counter

from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel


DIMENSIONS = ("frequency", "volume", "concurrency", "novelty")
LEVELS = (0.249, 0.199, 0.149, 0.129)
DURATION = 300.0
SAMPLE_PERIOD = 1.0


def _expected_throttle(deviation: float) -> float:
    if deviation >= 0.20:
        return 0.0
    if deviation <= 0.12:
        return 1.0
    progress = (deviation - 0.12) / (0.20 - 0.12)
    return max(0.0, 1.0 - progress * progress)


def _mem_available_bytes() -> int | None:
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError):
        return None
    return None


def _total_memory_bytes() -> int | None:
    try:
        with open("/proc/meminfo", encoding="utf-8") as handle:
            for line in handle:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
    except (OSError, ValueError):
        return None
    return None


def _runtime_fingerprint() -> dict[str, object]:
    return {
        "python": platform.python_version(),
        "os": platform.platform(),
        "kernel": platform.release(),
        "cpu_model": platform.processor() or None,
        "logical_cpus": os.cpu_count(),
        "total_memory_bytes": _total_memory_bytes(),
        "available_memory_bytes": _mem_available_bytes(),
        "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
    }


def _rss_bytes() -> int | None:
    if resource is None:
        return None
    # Linux reports ru_maxrss in KiB; macOS reports bytes.
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value * 1024 if platform.system() == "Linux" else value)


def test_instrumented_one_dimension_sustained_five_minute_limiter_profile() -> None:
    """Repeat the four fixed levels while recording resource measurements."""
    guard = FlowGuard({name: 100.0 for name in DIMENSIONS})
    baseline = guard.baseline
    fingerprint = _runtime_fingerprint()
    trace: list[str] = []

    for deviation in LEVELS:
        target = 100.0 * (1.0 + deviation)
        started = time.monotonic()
        cpu_started = time.process_time()
        samples = 0
        blocked = 0
        throttles: list[float] = []
        peak_rss = _rss_bytes()
        min_available = fingerprint["available_memory_bytes"]
        max_load = 0.0

        while time.monotonic() - started < DURATION:
            observed = {name: 100.0 for name in DIMENSIONS}
            observed["frequency"] = target
            decision = guard.evaluate(observed)
            expected = _expected_throttle(deviation)
            assert decision.allowed is (deviation < 0.20)
            assert abs(decision.throttle - expected) <= 1e-12
            assert abs(decision.max_deviation - deviation) <= 1e-12
            throttles.append(decision.throttle)
            blocked += int(not decision.allowed)
            samples += 1

            current_rss = _rss_bytes()
            if current_rss is not None:
                peak_rss = (
                    current_rss
                    if peak_rss is None
                    else max(peak_rss, current_rss)
                )
            available = _mem_available_bytes()
            if available is not None:
                min_available = (
                    available
                    if min_available is None
                    else min(min_available, available)
                )
            if hasattr(os, "getloadavg"):
                max_load = max(max_load, os.getloadavg()[0])
            time.sleep(SAMPLE_PERIOD)

        elapsed = time.monotonic() - started
        cpu_seconds = time.process_time() - cpu_started
        cpu_count = int(fingerprint["logical_cpus"] or 1)
        process_cpu_percent_of_host = 100.0 * cpu_seconds / elapsed / cpu_count
        trace.append(
            json.dumps(
                {
                    "dimension": "frequency",
                    "deviation": deviation,
                    "load_percent_of_baseline": (1.0 + deviation) * 100.0,
                    "duration_seconds": DURATION,
                    "elapsed_seconds": round(elapsed, 3),
                    "samples": samples,
                    "blocked_samples": blocked,
                    "min_throttle": min(throttles),
                    "max_throttle": max(throttles),
                    "expected_throttle": _expected_throttle(deviation),
                    "process_cpu_seconds": round(cpu_seconds, 3),
                    "process_cpu_percent_of_host": round(process_cpu_percent_of_host, 3),
                    "peak_rss_bytes": peak_rss,
                    "min_available_memory_bytes": min_available,
                    "max_load_1m": round(max_load, 3),
                },
                sort_keys=True,
            )
        )

    assert guard.baseline == baseline
    print("RUNTIME_FINGERPRINT_BEGIN")
    print(json.dumps(fingerprint, sort_keys=True))
    print("RUNTIME_FINGERPRINT_END")
    print("INSTRUMENTED_LIMITER_PROFILE_BEGIN")
    print("\n".join(trace))
    print("INSTRUMENTED_LIMITER_PROFILE_END")


def test_instrumented_five_hundred_thread_oversized_payload_stability() -> None:
    """Measure host/process resources around the 500-thread stress boundary."""
    fortress = CyberFortress(SignedIPCChannel(b"shared-secret"))
    malformed_payload = b'{"envelope":"' + (b"X" * 10**6)
    results: Counter[str] = Counter()
    unexpected: list[BaseException] = []
    lock = threading.Lock()
    barrier = threading.Barrier(500)
    fingerprint = _runtime_fingerprint()
    rss_before = _rss_bytes()
    available_before = _mem_available_bytes()
    load_before = os.getloadavg()[0] if hasattr(os, "getloadavg") else None
    cpu_started = time.process_time()
    started = time.monotonic()

    def trigger_heavy_load() -> None:
        try:
            barrier.wait(timeout=30.0)
            fortress.receive("203.0.113.43", malformed_payload, now=time.time())
        except SecurityError as exc:
            with lock:
                results["SecurityError"] += 1
                results[str(exc)] += 1
        except BaseException as exc:  # pragma: no cover - unexpected failures
            with lock:
                unexpected.append(exc)

    threads = [threading.Thread(target=trigger_heavy_load) for _ in range(500)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60.0)

    elapsed = time.monotonic() - started
    cpu_seconds = time.process_time() - cpu_started
    alive = [thread for thread in threads if thread.is_alive()]
    rss_after = _rss_bytes()
    available_after = _mem_available_bytes()
    load_after = os.getloadavg()[0] if hasattr(os, "getloadavg") else None

    assert not alive, f"{len(alive)} worker threads remained alive"
    assert not unexpected, f"unexpected worker exceptions: {unexpected!r}"
    assert results["SecurityError"] == 500
    assert elapsed < 60.0

    cpu_count = int(fingerprint["logical_cpus"] or 1)
    process_cpu_percent_of_host = 100.0 * cpu_seconds / elapsed / cpu_count
    print("RUNTIME_500T_BEGIN")
    print(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "threads": 500,
                "payload_bytes": len(malformed_payload),
                "elapsed_seconds": round(elapsed, 3),
                "process_cpu_seconds": round(cpu_seconds, 3),
                "process_cpu_percent_of_host": round(process_cpu_percent_of_host, 3),
                "rss_before_bytes": rss_before,
                "rss_after_bytes": rss_after,
                "peak_rss_bytes": _rss_bytes(),
                "available_memory_before_bytes": available_before,
                "available_memory_after_bytes": available_after,
                "load_1m_before": load_before,
                "load_1m_after": load_after,
                "security_errors": results["SecurityError"],
                "unexpected_exceptions": len(unexpected),
            },
            sort_keys=True,
        )
    )
    print("RUNTIME_500T_END")
