"""Workflow orchestration built on the validation gate.

This layer translates validation results into project-workflow actions. It has
no direct dependency on SMTP, Jira, Trello, GUI, or the thermal engine.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from .input_contract import CalculationScope, InputStatus, ThermalZoneInput
from .validation_gate import MissingParameter, ValidationResult, validate_thermal_inputs


@dataclass(frozen=True)
class WorkflowAction:
    kind: str
    target: str
    payload: dict


class WorkflowAdapter(Protocol):
    """External adapter contract implemented by application infrastructure."""

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
    """Validate a zone and optionally dispatch resulting workflow actions."""
    validation = validate_thermal_inputs(inputs)
    actions = build_actions(validation, project_id, inputs.zone_id)
    for adapter in adapters or []:
        for action in actions:
            adapter.dispatch(action)
    return validation
