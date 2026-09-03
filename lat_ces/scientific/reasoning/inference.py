from __future__ import annotations
from .rule import ScientificRule

class InferenceEngine:
    def apply(self, rule: ScientificRule, premises: tuple[str, ...]) -> dict[str, object]:
        if not premises:
            raise ValueError("Missing premises")
        return {"rule": rule.rule_id, "premises": tuple(premises)}
