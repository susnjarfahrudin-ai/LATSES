from __future__ import annotations

class ApprovalWorkflow:
    ORDER = ("PROPOSAL", "REVIEW", "VALIDATION", "APPROVAL", "DEPLOYMENT")

    def approve(self, proposal: object, validator: object) -> dict[str, object]:
        if proposal is None or validator is None:
            raise ValueError("Approval requires proposal and validator")
        return {"proposal": proposal, "approved_by": validator, "status": "APPROVED"}
