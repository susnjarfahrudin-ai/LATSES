from __future__ import annotations
from .synthesis_object import ScientificSynthesisObject
from .synthesis_method import SynthesisMethod
from .model_builder import ScientificModelBuilder
from .confidence import calculate_synthesis_confidence

class ScientificKnowledgeSynthesisEngine:
    def __init__(self) -> None:
        self.methods: dict[str, SynthesisMethod] = {}
        self.model_builder = ScientificModelBuilder()

    def register_method(self, method: SynthesisMethod) -> None:
        if method.method_id in self.methods and self.methods[method.method_id] != method:
            raise ValueError(f"Duplicate synthesis method: {method.method_id}")
        self.methods[method.method_id] = method

    def synthesize(self, method_id: str, knowledge: tuple[str, ...], *, output: str, confidence_values: tuple[float, ...] = (), trace: tuple[str, ...] = ()) -> ScientificSynthesisObject:
        if method_id not in self.methods:
            raise KeyError(f"Unknown synthesis method: {method_id}")
        self.model_builder.build(knowledge)
        if not trace:
            raise ValueError("Synthesis requires a trace")
        confidence = calculate_synthesis_confidence(confidence_values) if confidence_values else 0.0
        return ScientificSynthesisObject(knowledge, method_id, output, confidence, trace=trace)
