from __future__ import annotations

from typing import Dict

from lat_ces.scientific.dimensions.dimension import (
    DIMENSIONLESS,
    Dimension,
    LENGTH,
    MASS,
    TEMPERATURE,
    TIME,
)
from lat_ces.scientific.equations.engine import PhysicalDomainError, PhysicalEquation
from lat_ces.scientific.quantity import PhysicalQuantity
from lat_ces.scientific.units.units import Unit


VELOCITY = LENGTH / TIME
DYNAMIC_VISCOSITY = MASS / (LENGTH * TIME)
KINEMATIC_VISCOSITY = LENGTH**2 / TIME
THERMAL_CONDUCTIVITY = MASS * LENGTH / (TIME**3 * TEMPERATURE)
HEAT_TRANSFER_COEFFICIENT = MASS / (TIME**3 * TEMPERATURE)


_DIMENSIONLESS_UNIT = Unit("dimensionless", "-", DIMENSIONLESS)


def _dimensionless(quantity: PhysicalQuantity) -> PhysicalQuantity:
    return PhysicalQuantity(quantity.value, quantity.uncertainty, _DIMENSIONLESS_UNIT)


class ReynoldsNumberEquation(PhysicalEquation):
    """Re = rho * v * L / mu."""

    @property
    def name(self) -> str:
        return "Reynolds number (Re = rho * v * L / mu)"

    @property
    def expected_dimensions(self) -> Dict[str, Dimension]:
        return {
            "density": MASS / (LENGTH**3),
            "velocity": VELOCITY,
            "characteristic_length": LENGTH,
            "dynamic_viscosity": DYNAMIC_VISCOSITY,
        }

    def _check_physical_domain(self, kwargs: Dict[str, PhysicalQuantity]) -> None:
        if kwargs["density"].value <= 0.0:
            raise PhysicalDomainError("Density must be greater than zero.")
        if kwargs["velocity"].value < 0.0:
            raise PhysicalDomainError("Velocity cannot be negative.")
        if kwargs["characteristic_length"].value <= 0.0:
            raise PhysicalDomainError("Characteristic length must be greater than zero.")
        if kwargs["dynamic_viscosity"].value <= 0.0:
            raise PhysicalDomainError("Dynamic viscosity must be greater than zero.")

    def _compute(self, kwargs: Dict[str, PhysicalQuantity]) -> PhysicalQuantity:
        return _dimensionless(
            kwargs["density"]
            * kwargs["velocity"]
            * kwargs["characteristic_length"]
            / kwargs["dynamic_viscosity"]
        )


class MachNumberEquation(PhysicalEquation):
    """Ma = v / a."""

    @property
    def name(self) -> str:
        return "Mach number (Ma = v / a)"

    @property
    def expected_dimensions(self) -> Dict[str, Dimension]:
        return {"velocity": VELOCITY, "speed_of_sound": VELOCITY}

    def _check_physical_domain(self, kwargs: Dict[str, PhysicalQuantity]) -> None:
        if kwargs["velocity"].value < 0.0:
            raise PhysicalDomainError("Velocity cannot be negative.")
        if kwargs["speed_of_sound"].value <= 0.0:
            raise PhysicalDomainError("Speed of sound must be greater than zero.")

    def _compute(self, kwargs: Dict[str, PhysicalQuantity]) -> PhysicalQuantity:
        return _dimensionless(kwargs["velocity"] / kwargs["speed_of_sound"])


class PrandtlNumberEquation(PhysicalEquation):
    """Pr = nu / alpha."""

    @property
    def name(self) -> str:
        return "Prandtl number (Pr = nu / alpha)"

    @property
    def expected_dimensions(self) -> Dict[str, Dimension]:
        return {"kinematic_viscosity": KINEMATIC_VISCOSITY, "thermal_diffusivity": KINEMATIC_VISCOSITY}

    def _check_physical_domain(self, kwargs: Dict[str, PhysicalQuantity]) -> None:
        if kwargs["kinematic_viscosity"].value < 0.0:
            raise PhysicalDomainError("Kinematic viscosity cannot be negative.")
        if kwargs["thermal_diffusivity"].value <= 0.0:
            raise PhysicalDomainError("Thermal diffusivity must be greater than zero.")

    def _compute(self, kwargs: Dict[str, PhysicalQuantity]) -> PhysicalQuantity:
        return _dimensionless(kwargs["kinematic_viscosity"] / kwargs["thermal_diffusivity"])


class NusseltNumberEquation(PhysicalEquation):
    """Nu = h * L / k."""

    @property
    def name(self) -> str:
        return "Nusselt number (Nu = h * L / k)"

    @property
    def expected_dimensions(self) -> Dict[str, Dimension]:
        return {
            "heat_transfer_coefficient": HEAT_TRANSFER_COEFFICIENT,
            "characteristic_length": LENGTH,
            "thermal_conductivity": THERMAL_CONDUCTIVITY,
        }

    def _check_physical_domain(self, kwargs: Dict[str, PhysicalQuantity]) -> None:
        if kwargs["heat_transfer_coefficient"].value < 0.0:
            raise PhysicalDomainError("Heat-transfer coefficient cannot be negative.")
        if kwargs["characteristic_length"].value <= 0.0:
            raise PhysicalDomainError("Characteristic length must be greater than zero.")
        if kwargs["thermal_conductivity"].value <= 0.0:
            raise PhysicalDomainError("Thermal conductivity must be greater than zero.")

    def _compute(self, kwargs: Dict[str, PhysicalQuantity]) -> PhysicalQuantity:
        return _dimensionless(
            kwargs["heat_transfer_coefficient"]
            * kwargs["characteristic_length"]
            / kwargs["thermal_conductivity"]
        )


class BiotNumberEquation(PhysicalEquation):
    """Bi = h * Lc / k."""

    @property
    def name(self) -> str:
        return "Biot number (Bi = h * Lc / k)"

    @property
    def expected_dimensions(self) -> Dict[str, Dimension]:
        return {
            "heat_transfer_coefficient": HEAT_TRANSFER_COEFFICIENT,
            "characteristic_length": LENGTH,
            "thermal_conductivity": THERMAL_CONDUCTIVITY,
        }

    def _check_physical_domain(self, kwargs: Dict[str, PhysicalQuantity]) -> None:
        if kwargs["heat_transfer_coefficient"].value < 0.0:
            raise PhysicalDomainError("Heat-transfer coefficient cannot be negative.")
        if kwargs["characteristic_length"].value <= 0.0:
            raise PhysicalDomainError("Characteristic length must be greater than zero.")
        if kwargs["thermal_conductivity"].value <= 0.0:
            raise PhysicalDomainError("Thermal conductivity must be greater than zero.")

    def _compute(self, kwargs: Dict[str, PhysicalQuantity]) -> PhysicalQuantity:
        return _dimensionless(
            kwargs["heat_transfer_coefficient"]
            * kwargs["characteristic_length"]
            / kwargs["thermal_conductivity"]
        )


class FourierNumberEquation(PhysicalEquation):
    """Fo = alpha * t / Lc^2."""

    @property
    def name(self) -> str:
        return "Fourier number (Fo = alpha * t / Lc²)"

    @property
    def expected_dimensions(self) -> Dict[str, Dimension]:
        return {
            "thermal_diffusivity": KINEMATIC_VISCOSITY,
            "time": TIME,
            "characteristic_length": LENGTH,
        }

    def _check_physical_domain(self, kwargs: Dict[str, PhysicalQuantity]) -> None:
        if kwargs["thermal_diffusivity"].value < 0.0:
            raise PhysicalDomainError("Thermal diffusivity cannot be negative.")
        if kwargs["time"].value < 0.0:
            raise PhysicalDomainError("Time cannot be negative.")
        if kwargs["characteristic_length"].value <= 0.0:
            raise PhysicalDomainError("Characteristic length must be greater than zero.")

    def _compute(self, kwargs: Dict[str, PhysicalQuantity]) -> PhysicalQuantity:
        length = kwargs["characteristic_length"]
        return _dimensionless(
            kwargs["thermal_diffusivity"] * kwargs["time"] / (length**2)
        )


__all__ = [
    "ReynoldsNumberEquation",
    "MachNumberEquation",
    "PrandtlNumberEquation",
    "NusseltNumberEquation",
    "BiotNumberEquation",
    "FourierNumberEquation",
]
