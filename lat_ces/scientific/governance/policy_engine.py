from __future__ import annotations
from .rules import GovernanceRule

class PolicyEngine:
    def check(self, action: str, rules: tuple[GovernanceRule, ...]) -> bool:
        if not action.strip() or not rules:
            return False
        return all(rule.status == "ACTIVE" for rule in rules)
