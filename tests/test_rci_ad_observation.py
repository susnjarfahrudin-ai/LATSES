from lat_ces.rci_ad.observation import observe_host_telemetry
from lat_ces.rci_ad.telemetry import HostTelemetry


def test_observation_forwards_exact_snapshot(monkeypatch):
    expected = HostTelemetry(
        timestamp=1.0,
        platform="test",
        cpu_model=None,
        logical_cpu=4,
        physical_cpu=2,
        cpu_percent=25.0,
        load_1m=None,
        ram_total_bytes=100,
        ram_available_bytes=40,
        ram_used_bytes=60,
        source="test",
    )
    captured = []

    monkeypatch.setattr(
        "lat_ces.rci_ad.observation.collect_host_telemetry",
        lambda interval: expected,
    )

    result = observe_host_telemetry(captured.append, interval=0)

    assert result is expected
    assert captured == [expected]


def test_observation_does_not_add_policy_or_limiter_behavior():
    assert callable(observe_host_telemetry)
    assert not hasattr(observe_host_telemetry, "limit")
    assert not hasattr(observe_host_telemetry, "throttle")
