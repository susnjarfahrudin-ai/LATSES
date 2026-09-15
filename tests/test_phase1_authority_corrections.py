from lat_ces.com.gateway import SecureGateway
from lat_ces.core.axioms import ConstitutionalAxiom
from lat_ces.gov.axiom import ConstitutionalEngine


def test_reality_is_reference_and_measurement_is_not_absolute_authority():
    statement = ConstitutionalAxiom.AXIOM_1_REALITY_SUPREMACY.lower()
    assert "krajnji referent" in statement
    assert "podliježu provjeri" in statement
    assert "samostalni autoritet" in statement


def test_secure_gateway_rejects_returned_constitutional_violations():
    governance = ConstitutionalEngine()
    governance.add_axiom("deny", lambda payload: False)
    gateway = SecureGateway(governance)

    try:
        gateway.process_request({"value": 1})
    except Exception as exc:
        assert "Gateway Access Denied" in str(exc)
    else:
        raise AssertionError("Gateway accepted a request despite a constitutional violation")


def test_secure_gateway_accepts_when_no_constitutional_violation_exists():
    governance = ConstitutionalEngine()
    governance.add_axiom("allow", lambda payload: True)
    gateway = SecureGateway(governance)

    assert gateway.process_request({"value": 1}) is True
