"""Stable GUI communication boundaries for LAT-CES.

This package defines communication contracts and thin adapters. It does not
own BuildingModel, engineering rules, verification, governance, provenance,
or external-tool state.
"""

from .contracts import (
    GUICommand,
    GUIEvent,
    GUIResult,
    GUIState,
    BoundaryStatus,
    ExternalHandoffContract,
    GUICommandAdapter,
    DomainModelAdapter,
    PresentationAdapter,
)
from .adapters import PreparedGUICommandAdapter, Scene1Adapter, ThreeDHandoffAdapter

__all__ = [
    "GUICommand",
    "GUIEvent",
    "GUIResult",
    "GUIState",
    "BoundaryStatus",
    "GUICommandAdapter",
    "DomainModelAdapter",
    "PresentationAdapter",
    "ExternalHandoffContract",
    "PreparedGUICommandAdapter",
    "Scene1Adapter",
    "ThreeDHandoffAdapter",
]
