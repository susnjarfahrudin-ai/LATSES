"""
LAT-CES Communication Core
Secure Gateway Interface Reference Implementation (LAT-COM-CORE-0012)
"""
from typing import Any, Dict

from lat_ces.gov.axiom import AxiomViolationError, ConstitutionalEngine


class SecureGateway:
    """
    Gatekeeper for external interactions, ensuring all requests adhere
    to constitutional constraints.
    """

    def __init__(self, governance: ConstitutionalEngine):
        self.governance = governance

    def process_request(self, payload: Dict[str, Any]) -> bool:
        """Process an external request with fail-closed constitutional validation."""
        try:
            violations = self.governance.verify_state(payload)
            if violations:
                raise AxiomViolationError(
                    "Constitutional validation failed: " + ", ".join(map(str, violations))
                )
            return True
        except Exception as e:
            raise Exception(f"Gateway Access Denied: {str(e)}") from e
