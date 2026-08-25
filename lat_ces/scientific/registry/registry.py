"""
LAT-CES Scientific Core
Scientific Knowledge Registry Reference Implementation (LAT-SCI-CORE-0020)
"""

from typing import Any, Dict

from lat_ces.scientific.units.dimension import Dimension
from lat_ces.scientific.units.unit import Unit


class RegistryError(Exception):
    """Base exception for Scientific Knowledge Registry operations."""

    pass


class ScientificKnowledgeRegistry:
    """
    Central registry for dimensions, units, physical constants, and SKO references.

    Constants are stored in this canonical registry; the legacy constants module
    remains a source of typed definitions, not a second registry authority.
    """

    def __init__(self):
        self._dimensions: Dict[str, Dimension] = {}
        self._units: Dict[str, Unit] = {}
        self._constants: Dict[str, Any] = {}

    def register_dimension(self, symbol: str, dimension: Dimension) -> None:
        if symbol in self._dimensions:
            raise RegistryError(f"Dimension '{symbol}' is already registered.")
        if not isinstance(dimension, Dimension):
            raise RegistryError("Object must be a valid Dimension instance.")
        self._dimensions[symbol] = dimension

    def get_dimension(self, symbol: str) -> Dimension:
        if symbol not in self._dimensions:
            raise RegistryError(f"Dimension '{symbol}' not found in registry.")
        return self._dimensions[symbol]

    def register_unit(self, symbol: str, unit: Unit) -> None:
        if symbol in self._units:
            raise RegistryError(f"Unit symbol '{symbol}' is already registered.")
        if not isinstance(unit, Unit):
            raise RegistryError("Object must be a valid Unit instance.")
        self._units[symbol] = unit

    def get_unit(self, symbol: str) -> Unit:
        if symbol not in self._units:
            raise RegistryError(f"Unit '{symbol}' not found in registry.")
        return self._units[symbol]

    def register_constant(self, symbol: str, constant: Any) -> None:
        if symbol in self._constants:
            raise RegistryError(f"Constant '{symbol}' is already registered.")
        if not hasattr(constant, "value") or not hasattr(constant, "unit"):
            raise RegistryError("Object must be a typed physical constant with value and unit.")
        self._constants[symbol] = constant

    def get_constant(self, symbol: str) -> Any:
        if symbol not in self._constants:
            raise RegistryError(f"Constant '{symbol}' not found in registry.")
        return self._constants[symbol]

    def clear(self) -> None:
        """Resets the registry state (primarily used in test teardowns)."""
        self._dimensions.clear()
        self._units.clear()
        self._constants.clear()
