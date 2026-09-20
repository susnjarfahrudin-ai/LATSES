from __future__ import annotations

from lat_ces.security.threat_score import ThreatScorePolicy


def test_whitelist_accepts_ipv4_with_port() -> None:
    policy = ThreatScorePolicy(whitelist=("10.0.0.0/8",))
    assert policy.is_whitelisted("10.0.0.8:5000")


def test_whitelist_accepts_bracketed_ipv6_with_port() -> None:
    policy = ThreatScorePolicy(whitelist=("2001:db8::/32",))
    assert policy.is_whitelisted("[2001:db8::8]:5000")


def test_non_ip_ingress_identity_is_not_whitelisted() -> None:
    policy = ThreatScorePolicy(whitelist=("10.0.0.0/8", "::1/128"))
    assert not policy.is_whitelisted("process-peer-a")


def test_malformed_endpoint_is_not_whitelisted() -> None:
    policy = ThreatScorePolicy(whitelist=("10.0.0.0/8",))
    assert not policy.is_whitelisted("10.0.0.8:not-a-port")
