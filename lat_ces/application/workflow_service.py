"""Application orchestration for thermal validation workflows.

The thermal package owns input contracts and validation truth. This module
converts that truth into workflow actions and optionally dispatches external
adapters supplied by the application layer.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from lat_ces.thermal.input_contract import ThermalZoneInput
from lat_ces.thermal.validation_gate import ValidationResult, validate_thermal_inputs


@dataclass(frozen=True)
class WorkflowAction:
    kind: str
    target: str
    payload: dict


class WorkflowAdapter(Protocol):
    def dispatch(self, action: WorkflowAction) -> None:
        ...


def build_actions(validation: ValidationResult, project_id: str, zone_id: str) -> List[WorkflowAction]:
    """Create side-effect-free workflow actions from a validation result."""
    actions: List[WorkflowAction] = []
    if validation.calculation_allowed:
        actions.append(
            WorkflowAction(
                kind="CALCULATION_READY",
                target=project_id,
                payload={"scope": validation.scope.value, "zone_id": zone_id},
            )
        )
        return actions

    for item in [*validation.missing_parameters, *validation.invalid_parameters, *validation.unverified_parameters]:
        actions.append(
            WorkflowAction(
                kind="INPUT_BLOCKER",
                target=item.responsible_role,
                payload={
                    "project_id": project_id,
                    "zone_id": zone_id,
                    "category": item.category,
                    "element_id": item.element_id,
                    "field": item.field,
                    "expected_unit": item.expected_unit,
                    "hint": item.hint,
                    "scope": validation.scope.value,
                    "status": validation.status.value,
                },
            )
        )
    return actions


def evaluate_zone(
    inputs: ThermalZoneInput,
    *,
    project_id: str,
    adapters: List[WorkflowAdapter] | None = None,
) -> ValidationResult:
    """Validate a zone and optionally dispatch application workflow adapters."""
    validation = validate_thermal_inputs(inputs)
    actions = build_actions(validation, project_id, inputs.zone_id)
    for adapter in adapters or []:
        for action in actions:
            adapter.dispatch(action)
    return validation


__all__ = ["WorkflowAction", "WorkflowAdapter", "build_actions", "evaluate_zone"]
