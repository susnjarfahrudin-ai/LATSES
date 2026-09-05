from __future__ import annotations
from .rule import ScientificRule
from .reasoning_object import ScientificReasoningObject
from .confidence import calculate_confidence

class ScientificKnowledgeReasoningEngine:
    def __init__(self) -> None:
        self.rules: dict[str, ScientificRule] = {}

    def register_rule(self, rule: ScientificRule) -> None:
        if rule.rule_id in self.rules and self.rules[rule.rule_id] != rule:
            raise ValueError(f"Duplicate reasoning rule: {rule.rule_id}")
        self.rules[rule.rule_id] = rule

    def reason(
        self,
        rule_id: str,
        premises: tuple[str, ...],
        conclusion: str,
        *,
        confidence_values: tuple[float, ...] = (),
        trace: tuple[str, ...] = (),
    ) -> ScientificReasoningObject:
        rule = self.rules.get(rule_id)
        if rule is None:
            raise KeyError(f"Unknown reasoning rule: {rule_id}")
        if not premises:
            raise ValueError("No conclusion without premises")
        if not trace:
            raise ValueError("Every reasoning result requires a trace")
        confidence = calculate_confidence(confidence_values) if confidence_values else 0.0
        return ScientificReasoningObject(premises, rule.rule_id, conclusion, confidence, trace=trace)
