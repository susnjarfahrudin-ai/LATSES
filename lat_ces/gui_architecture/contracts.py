"""Stable communication contracts for the LAT-CES GUI boundary.

The contracts intentionally carry no engineering authority. They describe
messages crossing the GUI boundary; domain ownership remains outside the GUI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence


class BoundaryStatus(str, Enum):
    PREPARED = "PREPARED"
    CONNECTED = "CONNECTED"
    NOT_YET_CONNECTED = "NOT_YET_CONNECTED"


@dataclass(frozen=True)
class GUICommand:
    """User intent expressed without exposing an internal core API."""

    command: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    source: str = "GUI"


@dataclass(frozen=True)
class GUIEvent:
    """Event returned toward presentation/workflow state."""

    event: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    source: str = "LAT-CES"


@dataclass(frozen=True)
class GUIResult:
    """Transport result; it is not an engineering result or authority."""

    status: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    events: Sequence[GUIEvent] = field(default_factory=tuple)


@dataclass(frozen=True)
class GUIState:
    """Presentation/workflow state only; never a second model authority."""

    view: str = ""
    selected_id: str | None = None
    values: Mapping[str, Any] = field(default_factory=dict)


class GUICommandAdapter(Protocol):
    """Boundary for translating GUI intent into a future core command path."""

    def dispatch(self, command: GUICommand) -> GUIResult:
        ...


class DomainModelAdapter(Protocol):
    """Boundary for future canonical-domain/model communication."""

    def submit(self, command: GUICommand) -> GUIResult:
        ...


class PresentationAdapter(Protocol):
    """Boundary for translating core results/events into GUI presentation data."""

    def present(self, result: GUIResult) -> GUIResult:
        ...


class ExternalHandoffContract(Protocol):
    """Boundary for approved handoff from LAT-CES to an external system."""

    status: BoundaryStatus

    def export(self, model: Any, target: str) -> GUIResult:
        ...
