import math

import pytest

from lat_ces.rci_ad.canonical_observation import CanonicalObservation
from lat_ces.rci_ad.integrity_state import IntegrityState
from lat_ces.rci_ad.trust_state import TrustState


def make_observation(**overrides):
    values = dict(
        source_id="flowguard", source_type="FLOW", device_id=None,
        interface_id="ipc0", module_id="security", data_type="frequency",
        timestamp=1000.0, measurement=120.0, unit="events/s", direction="IN",
        protocol="IPC", rate=120.0, size=None, confidence=1.0, version="1",
        integrity_state=IntegrityState.VERIFIED, trust_state=TrustState.UNTRUSTED,
        sequence=1,
    )
    values.update(overrides)
    return CanonicalObservation(**values)


def test_observation_is_immutable():
    observation = make_observation()
    with pytest.raises(Exception):
        observation.measurement = 1.0


def test_integrity_and_trust_are_independent():
    observation = make_observation()
    assert observation.integrity_state is IntegrityState.VERIFIED
    assert observation.trust_state is TrustState.UNTRUSTED


@pytest.mark.parametrize("field,value", [
    ("timestamp", math.nan), ("measurement", math.inf), ("rate", -1.0),
    ("size", math.nan), ("confidence", 1.1),
])
def test_invalid_numeric_evidence_is_rejected(field, value):
    with pytest.raises(ValueError):
        make_observation(**{field: value})


def test_sequence_rejects_bool_and_negative_values():
    with pytest.raises(ValueError):
        make_observation(sequence=True)
    with pytest.raises(ValueError):
        make_observation(sequence=-1)


def test_empty_identity_fields_are_rejected():
    with pytest.raises(ValueError):
        make_observation(source_id="")
