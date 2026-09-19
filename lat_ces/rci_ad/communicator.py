"""Read-only canonical communication bus."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable
from .canonical_observation import CanonicalObservation

@dataclass(frozen=True)
class RoutedMessage:
    observation: CanonicalObservation
    destination: str

class Communicator:
    def __init__(self, validator: Callable[[CanonicalObservation], bool] | None=None):
        self._validator=validator or (lambda _: True)
        self._routes: dict[str, tuple[str,...]]={}
        self._messages: list[RoutedMessage]=[]
    def register_route(self, source_type: str, destinations: Iterable[str]) -> None:
        self._routes[source_type]=tuple(destinations)
    def publish(self, observation: CanonicalObservation) -> tuple[RoutedMessage,...]:
        if not self._validator(observation): raise ValueError("observation failed communicator validation")
        destinations=self._routes.get(observation.source_type,())
        messages=tuple(RoutedMessage(observation,d) for d in destinations)
        self._messages.extend(messages)
        return messages
    def messages(self)->tuple[RoutedMessage,...]: return tuple(self._messages)
    def routes(self)->dict[str,tuple[str,...]]: return dict(self._routes)
