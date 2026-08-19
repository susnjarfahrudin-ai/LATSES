"""Building-first LAT-CES interface navigation contract.

This module defines the user-facing construction sequence independently from
Tkinter widgets.  The desktop GUI can consume the contract without creating a
second Building Model or a parallel source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class BuildingStage(IntEnum):
    """Canonical visual workflow presented to the LAT-CES user."""

    ROOF = 1
    LEVEL = 2
    FLOOR_PLAN = 3
    SECTION = 4
    MODEL_3D = 5


@dataclass(frozen=True)
class StageDefinition:
    stage: BuildingStage
    title: str
    description: str
    required_before: BuildingStage | None = None


BUILDING_STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(BuildingStage.ROOF, "Krov", "Vrsta krova, konstrukcija, pokrov, podkonstrukcija, oslonac i tlocrtne dimenzije."),
    StageDefinition(BuildingStage.LEVEL, "Sprat", "Raspored prostorija, visina, zidovi, izolacija, obloge i stolarija.", BuildingStage.ROOF),
    StageDefinition(BuildingStage.FLOOR_PLAN, "Tlocrt", "Dimenzionalni tlocrt i prostorni raspored etaže.", BuildingStage.LEVEL),
    StageDefinition(BuildingStage.SECTION, "Presjek", "Vertikalni presjek kroz etaže, visine, konstrukciju i krov.", BuildingStage.FLOOR_PLAN),
    StageDefinition(BuildingStage.MODEL_3D, "3D", "Sastavljeni Building Model spreman za instalacije i naučne sisteme.", BuildingStage.SECTION),
)


def stage_titles() -> tuple[str, ...]:
    """Return titles in canonical presentation order."""
    return tuple(item.title for item in BUILDING_STAGES)


def can_enter(stage: BuildingStage, completed: set[BuildingStage]) -> bool:
    """Return whether all prerequisite stages for *stage* are completed."""
    definition = next(item for item in BUILDING_STAGES if item.stage is stage)
    return definition.required_before is None or definition.required_before in completed
