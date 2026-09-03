"""Standards references attached to product and building-model data.

This registry stores references and applicability metadata only. It never
reproduces copyrighted normative text and never turns a standard reference
into an engineering decision by itself.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class StandardReference:
    """A versioned reference to a normative or classification document."""

    organization: str
    designation: str
    edition: str | None = None
    title: str | None = None
    scope: str | None = None
    source_uri: str | None = None
    applicable_to: Tuple[str, ...] = ()

    @property
    def key(self) -> str:
        return f"{self.organization}:{self.designation}:{self.edition or 'unspecified'}"

    def __post_init__(self) -> None:
        if not self.organization.strip() or not self.designation.strip():
            raise ValueError("standard organization and designation are required")


@dataclass
class StandardsRegistry:
    """Small registry for stable references used by engineering adapters."""

    _standards: dict[str, StandardReference] = field(default_factory=dict)

    def add(self, reference: StandardReference) -> None:
        if reference.key in self._standards:
            raise ValueError(f"duplicate standard reference: {reference.key}")
        self._standards[reference.key] = reference

    def get(self, key: str) -> StandardReference:
        try:
            return self._standards[key]
        except KeyError as exc:
            raise KeyError(f"unknown standard reference: {key}") from exc

    def for_element(self, element_type: str) -> Tuple[StandardReference, ...]:
        return tuple(
            reference
            for reference in self._standards.values()
            if not reference.applicable_to or element_type in reference.applicable_to
        )
