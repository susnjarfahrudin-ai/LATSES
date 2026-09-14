from __future__ import annotations

from lat_ces.scientific.governance.authority import Authority


class ApprovalWorkflow:
    ORDER = ("PROPOSAL", "REVIEW", "VALIDATION", "APPROVAL", "DEPLOYMENT")

    def approve(self, proposal: object, validator: Authority) -> dict[str, object]:
        if proposal is None or validator is None:
            raise ValueError("Approval requires proposal and validator")
        if not isinstance(validator, Authority):
            raise TypeError("Approval requires an explicit Authority")
        if validator.action != "APPROVE" or not validator.is_valid_now():
            raise PermissionError("Validator does not hold valid approval authority")
        return {
            "proposal": proposal,
            "approved_by": validator.identity,
            "authority_grant_id": validator.grant_id,
            "status": "APPROVED",
        }
