"""Long-running limiter measurement and concurrent stress probes.

These are measurement-only adversarial tests. They do not modify production
security state or learn a new baseline from traffic.
"""
from __future__ import annotations

import json
import threading
import time
from collections import Counter

from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel


DIMENSIONS = ("frequency", "volume", "concurrency", "novelty")


def _expected_throttle(deviation: float) -> float:
    if deviation >= 0.20:
        return 0.0
    if deviation <= 0.12:
        return 1.0
    progress = (deviation - 0.12) / (0.20 - 0.12)
    return max(0.0, 1.0 - progress * progress)


def test_one_dimension_sustained_five_minute_limiter_profile() -> None:
    """Hold frequency at four fixed deviations for 5 minutes each.

    The other three dimensions remain exactly at baseline. A JSONL trace is
    accumulated in memory and emitted at the end so CI logs contain a compact,
    machine-readable mathematical record without adding a runtime log writer.
    """
    guard = FlowGuard({name: 100.0 for name in DIMENSIONS})
    baseline = guard.baseline
    levels = (0.249, 0.199, 0.149, 0.129)
    duration = 300.0
    sample_period = 1.0
    trace: list[str] = []

    for deviation in levels:
        target = 100.0 * (1.0 + deviation)
        started = time.monotonic()
        samples = 0
        throttles: list[float] = []
        blocked = 0
        while time.monotonic() - started < duration:
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
            time.sleep(sample_period)

        summary = {
            "dimension": "frequency",
            "deviation": deviation,
            "load_percent_of_baseline": (1.0 + deviation) * 100.0,
            "duration_seconds": duration,
            "samples": samples,
            "blocked_samples": blocked,
            "min_throttle": min(throttles),
            "max_throttle": max(throttles),
            "expected_throttle": _expected_throttle(deviation),
        }
        trace.append(json.dumps(summary, sort_keys=True))

    assert guard.baseline == baseline
    print("LIMITER_PROFILE_BEGIN")
    print("\n".join(trace))
    print("LIMITER_PROFILE_END")


def test_five_hundred_thread_oversized_payload_stability() -> None:
    """Apply the supplied 500-thread / 1-million-character stress pattern.

    The 1 MiB malformed payload is shared between workers to avoid turning the
    test itself into a 500 MiB allocation attack. All 500 workers execute the
    real CyberFortress receive boundary concurrently; expected security
    rejections are recorded, while unexpected exceptions fail the test.
    """
    fortress = CyberFortress(SignedIPCChannel(b"shared-secret"))
    malformed_payload = (b"{\"envelope\":\"" + (b"X" * 10**6))
    results: Counter[str] = Counter()
    unexpected: list[BaseException] = []
    lock = threading.Lock()
    barrier = threading.Barrier(500)

    def trigger_heavy_load() -> None:
        try:
            barrier.wait(timeout=30.0)
            fortress.receive("203.0.113.43", malformed_payload, now=time.time())
        except SecurityError as exc:
            with lock:
                results["SecurityError"] += 1
                results[str(exc)] += 1
        except BaseException as exc:  # pragma: no cover - only unexpected failures
            with lock:
                unexpected.append(exc)

    threads = [threading.Thread(target=trigger_heavy_load) for _ in range(500)]
    started = time.monotonic()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=60.0)

    elapsed = time.monotonic() - started
    alive = [thread for thread in threads if thread.is_alive()]
    assert not alive, f"{len(alive)} worker threads remained alive"
    assert not unexpected, f"unexpected worker exceptions: {unexpected!r}"
    assert results["SecurityError"] == 500
    assert elapsed < 60.0
    print(f"EXTREME_LOAD threads=500 payload_bytes={len(malformed_payload)} elapsed_seconds={elapsed:.3f}")
    print(f"EXTREME_LOAD_RESULTS {json.dumps(dict(results), sort_keys=True)}")
