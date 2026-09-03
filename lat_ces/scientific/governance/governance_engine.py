from __future__ import annotations
from .rules import GovernanceRule

class ScientificKnowledgeGovernanceEngine:
    def __init__(self) -> None:
        self.rules: list[GovernanceRule] = []
        self.audit: list[object] = []

    def register_rule(self, rule: GovernanceRule) -> None:
        if any(item.rule_id == rule.rule_id and item != rule for item in self.rules):
            raise ValueError(f"Duplicate governance rule: {rule.rule_id}")
        if rule not in self.rules:
            self.rules.append(rule)

    def evaluate_change(self, change: object) -> dict[str, object]:
        if change is None:
            raise ValueError("Governance change proposal cannot be empty")
        return {"change": change, "status": "UNDER_REVIEW"}
