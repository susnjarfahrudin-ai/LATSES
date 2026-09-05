import json
import platform

from lat_ces.rci_ad.telemetry import HostTelemetry, collect_host_telemetry


def test_host_telemetry_is_platform_neutral():
    telemetry = collect_host_telemetry(interval=0)

    assert isinstance(telemetry, HostTelemetry)
    assert telemetry.platform == platform.system()
    assert telemetry.logical_cpu is None or telemetry.logical_cpu >= 1
    assert telemetry.ram_total_bytes is None or telemetry.ram_total_bytes > 0
    assert telemetry.ram_available_bytes is None or telemetry.ram_available_bytes >= 0
    assert telemetry.cpu_percent is None or 0 <= telemetry.cpu_percent <= 100
    assert telemetry.load_1m is None or telemetry.load_1m >= 0


def test_unavailable_metrics_are_explicit_not_fabricated():
    telemetry = HostTelemetry(
        timestamp=1.0,
        platform="Windows",
        cpu_model=None,
        logical_cpu=8,
        physical_cpu=None,
        cpu_percent=None,
        load_1m=None,
        ram_total_bytes=None,
        ram_available_bytes=None,
        ram_used_bytes=None,
        source="test",
    )

    payload = telemetry.to_dict()
    assert payload["cpu_percent"] is None
    assert payload["load_1m"] is None
    assert payload["ram_total_bytes"] is None
    assert payload["physical_cpu"] is None
    json.dumps(payload)
