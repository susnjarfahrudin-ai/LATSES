from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping

from lat_ces.scientific.governance.governance_engine import ScientificKnowledgeGovernanceEngine

from .reason_codes import ApplicabilityReason
from .registry import ModelRegistry, ModelStatus


class ApplicabilityStatus(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INVALID_INPUT = "INVALID_INPUT"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    MODEL_SUPERSEDED = "MODEL_SUPERSEDED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    CONTRACT_INVALID = "CONTRACT_INVALID"


@dataclass(frozen=True)
class ApplicabilityRequest:
    model_id: str
    context: Mapping[str, object] | None = None
    inputs: Mapping[str, object] | None = None
    evidence: Mapping[str, object] | None = None
    model_version: str | None = None


@dataclass(frozen=True)
class ApplicabilityResult:
    status: ApplicabilityStatus
    applicable: bool
    model_id: str
    model_version: str | None
    reason_code: ApplicabilityReason
    rationale: str
    violations: tuple[str, ...] = ()
    validated_inputs: tuple[str, ...] = ()

    @property
    def is_applicable(self) -> bool:
        return self.applicable


class ApplicabilityEvaluator:
    """Evaluate model applicability without executing the model."""

    def __init__(
        self,
        registry: ModelRegistry,
        governance_engine: ScientificKnowledgeGovernanceEngine | None = None,
    ) -> None:
        self.registry = registry
        self.governance_engine = governance_engine

    def evaluate(self, request: ApplicabilityRequest) -> ApplicabilityResult:
        if not request.model_id.strip():
            return self._result(request, None, ApplicabilityStatus.MODEL_UNAVAILABLE, ApplicabilityReason.MODEL_NOT_REGISTERED, "No model identifier was supplied.")
        if not self.registry.has(request.model_id):
            return self._result(request, None, ApplicabilityStatus.MODEL_UNAVAILABLE, ApplicabilityReason.MODEL_NOT_REGISTERED, f"Model '{request.model_id}' is not registered.")

        entry = self.registry.get(request.model_id)
        if request.model_version is not None and request.model_version != entry.version:
            return self._result(request, entry.version, ApplicabilityStatus.MODEL_UNAVAILABLE, ApplicabilityReason.MODEL_VERSION_UNAVAILABLE, f"Requested model version '{request.model_version}' is unavailable; registered version is '{entry.version}'.")

        lifecycle = {
            ModelStatus.INACTIVE: (ApplicabilityStatus.NOT_APPLICABLE, ApplicabilityReason.MODEL_INACTIVE, f"Model '{request.model_id}' is inactive."),
            ModelStatus.BENCHED: (ApplicabilityStatus.NOT_APPLICABLE, ApplicabilityReason.MODEL_BENCHED, f"Model '{request.model_id}' is on the operational bench."),
            ModelStatus.RETIRED: (ApplicabilityStatus.NOT_APPLICABLE, ApplicabilityReason.MODEL_RETIRED, f"Model '{request.model_id}' is retired."),
            ModelStatus.INVALID: (ApplicabilityStatus.NOT_APPLICABLE, ApplicabilityReason.MODEL_INVALID, f"Model '{request.model_id}' is invalid."),
            ModelStatus.DEPRECATED: (ApplicabilityStatus.MODEL_SUPERSEDED, ApplicabilityReason.MODEL_SUPERSEDED, f"Model '{request.model_id}' is deprecated."),
            ModelStatus.SUPERSEDED: (ApplicabilityStatus.MODEL_SUPERSEDED, ApplicabilityReason.MODEL_SUPERSEDED, f"Model '{request.model_id}' has been superseded."),
        }
        if entry.status in lifecycle:
            status, reason, rationale = lifecycle[entry.status]
            return self._result(request, entry.version, status, reason, rationale)

        contract_issues = entry.contract.validate()
        if contract_issues:
            violations = tuple(f"{issue.code}: {issue.message}" for issue in contract_issues)
            return self._result(request, entry.version, ApplicabilityStatus.CONTRACT_INVALID, ApplicabilityReason.CONTRACT_VIOLATION, "Scientific model contract validation failed.", violations=violations)

        if request.context is None:
            return self._result(request, entry.version, ApplicabilityStatus.INSUFFICIENT_EVIDENCE, ApplicabilityReason.CONTEXT_MISSING, "No context was supplied for applicability evaluation.")
        if not request.context:
            return self._result(request, entry.version, ApplicabilityStatus.INSUFFICIENT_EVIDENCE, ApplicabilityReason.CONTEXT_INCOMPLETE, "The supplied context is incomplete.")

        required_inputs = {item.name for item in entry.metadata.inputs if item.required}
        supplied_inputs = set((request.inputs or {}).keys())
        missing = required_inputs - supplied_inputs
        if missing:
            return self._result(request, entry.version, ApplicabilityStatus.INVALID_INPUT, ApplicabilityReason.REQUIRED_INPUT_MISSING, "Required model inputs are missing.", violations=tuple(sorted(missing)))

        if entry.metadata.references and not request.evidence:
            return self._result(request, entry.version, ApplicabilityStatus.INSUFFICIENT_EVIDENCE, ApplicabilityReason.INSUFFICIENT_EVIDENCE, "The model declares references requiring supporting evidence.")

        if entry.metadata.references and request.evidence:
            unverified = tuple(
                key for key, evidence in request.evidence.items() if not self._has_verified_lineage(evidence)
            )
            if unverified:
                return self._result(
                    request,
                    entry.version,
                    ApplicabilityStatus.INSUFFICIENT_EVIDENCE,
                    ApplicabilityReason.INSUFFICIENT_EVIDENCE,
                    "Supporting evidence is present but its canonical verification record could not be resolved for the exact evidence identity and revision.",
                    violations=unverified,
                )

        return self._result(request, entry.version, ApplicabilityStatus.APPLICABLE, ApplicabilityReason.APPLICABLE_INPUTS_VALID, "Model applicability requirements are satisfied.", validated_inputs=tuple(sorted(required_inputs)))

    def _has_verified_lineage(self, evidence: object) -> bool:
        if self.governance_engine is None:
            return False
        return self.governance_engine.is_verified_by_record(evidence)

    @staticmethod
    def _result(request: ApplicabilityRequest, model_version: str | None, status: ApplicabilityStatus, reason_code: ApplicabilityReason, rationale: str, *, violations: tuple[str, ...] = (), validated_inputs: tuple[str, ...] = ()) -> ApplicabilityResult:
        return ApplicabilityResult(status=status, applicable=status is ApplicabilityStatus.APPLICABLE, model_id=request.model_id, model_version=model_version, reason_code=reason_code, rationale=rationale, violations=violations, validated_inputs=validated_inputs)
