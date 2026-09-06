import json
import pytest
from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.secure_ipc import SecurityError, SignedIPCChannel

def test_verified_defense_is_required_before_standby_import():
    source = AdaptiveDefense()
    standby = AdaptiveDefense()
    raw = source.observe_failure("ipc:authentication", "ipc-rejection", "bad mac", source="A")
    standby.quarantine(raw)
    with pytest.raises(ValueError):
        standby.import_verified(raw)
    verified = source.promote(raw, verification_sha="verification/restore")
    standby.import_verified(verified)
    assert standby.export_verified() == (verified,)

def test_cyber_fortress_records_failure_and_handoffs_only_verified_defense():
    primary = CyberFortress(SignedIPCChannel(b"shared-secret"))
    standby = CyberFortress(SignedIPCChannel(b"shared-secret"))
    packet = primary.ipc.pack({"operation": "read"}, sender_id="trusted")
    forged = json.loads(packet.decode("utf-8"))
    forged["mac"] = "0" * 64
    with pytest.raises(SecurityError):
        primary.receive("203.0.113.50", json.dumps(forged, separators=(",", ":")).encode(), now=100.0)
    records = primary.adaptive_defense.records()
    assert len(records) == 1
    assert not records[0].verified
    verified = primary.adaptive_defense.promote(records[0], verification_sha="verification/runtime")
    assert primary.handoff_verified_defense(standby) == 1
    assert standby.adaptive_defense.export_verified() == (verified,)
