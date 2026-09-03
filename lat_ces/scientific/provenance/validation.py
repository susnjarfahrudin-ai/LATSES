"""Validation rules SDPE-001 through SDPE-006."""
from __future__ import annotations

from typing import Any

from .data_object import ScientificDataObject
from .algorithm import AlgorithmReference
from .transformation import TransformationRecord


class ProvenanceValidationError(ValueError):
    """Raised when a provenance contract is incomplete or inconsistent."""


def validate_source(source: Any) -> bool:
    if source is None:
        raise ProvenanceValidationError("Missing source")
    for field in ("source_id", "source_type", "description"):
        if not str(getattr(source, field, "")).strip():
            raise ProvenanceValidationError(f"Source requires {field}")
    return True


def validate_data_object(data: ScientificDataObject) -> bool:
    if not data.data_id or not data.data_id.strip():
        raise ProvenanceValidationError("Scientific data requires an identity")
    validate_source(data.source)
    return True


def validate_algorithm(algorithm: AlgorithmReference) -> bool:
    if not algorithm.algorithm_id.strip() or not algorithm.version.strip():
        raise ProvenanceValidationError("Algorithm requires identity and version")
    return True


def validate_transformation(record: TransformationRecord) -> bool:
    if not all((record.input_id, record.operation, record.algorithm_id, record.output_id)):
        raise ProvenanceValidationError("Transformation requires input, operation, algorithm and output")
    return True


def validate_provenance_chain(chain: Any) -> bool:
    if not chain:
        raise ProvenanceValidationError("Empty provenance")
    for item in chain:
        if isinstance(item, ScientificDataObject):
            validate_data_object(item)
        elif isinstance(item, AlgorithmReference):
            validate_algorithm(item)
        elif isinstance(item, TransformationRecord):
            validate_transformation(item)
    return True
