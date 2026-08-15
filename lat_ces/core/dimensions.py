"""
LAT-CES Core: Dimension Engine (SI Base Units Algebra)
Dokumenti: LAT-SCI-CORE-0006 do LAT-SCI-CORE-0009
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Dimension:
    """Seven-base SI dimensional algebra with multiplication and division."""

    L: int = 0
    M: int = 0
    T: int = 0
    I: int = 0
    Theta: int = 0
    N: int = 0
    J: int = 0

    def __mul__(self, other: "Dimension") -> "Dimension":
        return Dimension(
            L=self.L + other.L,
            M=self.M + other.M,
            T=self.T + other.T,
            I=self.I + other.I,
            Theta=self.Theta + other.Theta,
            N=self.N + other.N,
            J=self.J + other.J,
        )

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return Dimension(
            L=self.L - other.L,
            M=self.M - other.M,
            T=self.T - other.T,
            I=self.I - other.I,
            Theta=self.Theta - other.Theta,
            N=self.N - other.N,
            J=self.J - other.J,
        )

    def __pow__(self, power: int | float) -> "Dimension":
        return Dimension(
            L=self.L * int(power),
            M=self.M * int(power),
            T=self.T * int(power),
            I=self.I * int(power),
            Theta=self.Theta * int(power),
            N=self.N * int(power),
            J=self.J * int(power),
        )

    def is_dimensionless(self) -> bool:
        return all(
            value == 0
            for value in [self.L, self.M, self.T, self.I, self.Theta, self.N, self.J]
        )


class UnitSKOError(ValueError):
    """Raised for invalid SKO status or incompatible unit conversions."""


class Unit:
    """Reference-style unit implementation with SKO metadata and conversion support."""

    VALID_STATUSES = {"DRAFT", "REVIEWED", "VERIFIED", "VALIDATED", "RELEASED"}

    def __init__(
        self,
        name: str,
        symbol: str,
        dimension: Dimension,
        scale_factor: float = 1.0,
        offset: float = 0.0,
        unit_uuid: str | None = None,
        status: str = "DRAFT",
    ):
        if status not in self.VALID_STATUSES:
            raise UnitSKOError(f"Nevažeći status: {status}. Dozvoljeni statusi: {self.VALID_STATUSES}")

        self._name = name
        self._symbol = symbol
        self._dimension = dimension
        self._scale_factor = float(scale_factor)
        self._offset = float(offset)
        self._uuid = unit_uuid or str(uuid4())
        self._status = status

    @property
    def name(self) -> str:
        return self._name

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def dimension(self) -> Dimension:
        return self._dimension

    @property
    def scale_factor(self) -> float:
        return self._scale_factor

    @property
    def offset(self) -> float:
        return self._offset

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def status(self) -> str:
        return self._status

    def set_status(self, new_status: str) -> None:
        if self._status == "RELEASED":
            raise UnitSKOError("Jedinica u stanju RELEASED je nepromjenjiva i ne može mijenjati status.")
        if new_status not in self.VALID_STATUSES:
            raise UnitSKOError(f"Nevažeći target status: {new_status}")
        self._status = new_status

    def _check_affine_safety(self) -> None:
        """Prevent arithmetic on units that carry an affine offset such as Celsius."""
        if self._offset != 0.0:
            raise UnitSKOError(
                f"Jedinica '{self.symbol}' ima temperaturni pomak (offset={self._offset}) "
                "i ne može učestvovati u algebri složenih jedinica bez prethodne konverzije."
            )

    def __mul__(self, other: "Unit" | int | float) -> "Unit":
        self._check_affine_safety()

        if isinstance(other, Unit):
            other._check_affine_safety()
            return Unit(
                name=f"({self.name} * {other.name})",
                symbol=f"{self.symbol}·{other.symbol}",
                dimension=self.dimension * other.dimension,
                scale_factor=self.scale_factor * other.scale_factor,
                status="DRAFT",
            )
        if isinstance(other, (int, float)):
            return Unit(
                name=f"Scaled({self.name})",
                symbol=self.symbol,
                dimension=self.dimension,
                scale_factor=self.scale_factor * float(other),
                offset=self.offset,
                status="DRAFT",
            )
        return NotImplemented

    def __rmul__(self, other: int | float) -> "Unit":
        return self.__mul__(other)

    def __truediv__(self, other: "Unit" | int | float) -> "Unit":
        self._check_affine_safety()

        if isinstance(other, Unit):
            other._check_affine_safety()
            return Unit(
                name=f"({self.name} / {other.name})",
                symbol=f"{self.symbol}/{other.symbol}",
                dimension=self.dimension / other.dimension,
                scale_factor=self.scale_factor / other.scale_factor,
                status="DRAFT",
            )
        if isinstance(other, (int, float)):
            return Unit(
                name=f"Scaled({self.name})",
                symbol=self.symbol,
                dimension=self.dimension,
                scale_factor=self.scale_factor / float(other),
                offset=self.offset,
                status="DRAFT",
            )
        return NotImplemented

    def __pow__(self, power: int | float) -> "Unit":
        self._check_affine_safety()

        return Unit(
            name=f"({self.name}^{power})",
            symbol=f"{self.symbol}^{power}",
            dimension=self.dimension ** power,
            scale_factor=float(self.scale_factor ** power),
            status="DRAFT",
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unit):
            return NotImplemented
        return (
            self.symbol == other.symbol
            and self.dimension == other.dimension
            and self.scale_factor == other.scale_factor
            and self.offset == other.offset
        )

    def __setattr__(self, name, value):
        if name in {"_status", "_name", "_symbol", "_dimension", "_scale_factor", "_offset", "_uuid"} and getattr(self, "_status", None) == "RELEASED":
            raise UnitSKOError("Jedinica u stanju RELEASED je nepromjenjiva i ne može mijenjati parametre.")
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return f"Unit(symbol='{self.symbol}', status='{self.status}', uuid='{self.uuid[:8]}...')"


SIUnit = Unit


DIMENSIONLESS = Dimension()
LENGTH = Dimension(L=1)
MASS = Dimension(M=1)
TIME = Dimension(T=1)
CURRENT = Dimension(I=1)
TEMPERATURE = Dimension(Theta=1)
AMOUNT = Dimension(N=1)
LUMINOUS_INTENSITY = Dimension(J=1)
VELOCITY = Dimension(L=1, T=-1)
DENSITY = Dimension(M=1, L=-3)
ACCELERATION = Dimension(L=1, T=-2)
FORCE = Dimension(M=1, L=1, T=-2)

# Canonical derived dimensions used by the scientific module layer.
AREA = LENGTH**2
FLOW_RATE = (LENGTH**3) / TIME
MASS_FLOW = MASS / TIME
PRESSURE = MASS / (LENGTH * (TIME**2))
POWER = (MASS * (LENGTH**2)) / (TIME**3)
SPECIFIC_HEAT = (LENGTH**2) / (TIME**2) / TEMPERATURE
HEAT_RATE = POWER
DYNAMIC_VISCOSITY = MASS / (LENGTH * TIME)

meter = Unit(name="meter", symbol="m", dimension=LENGTH, scale_factor=1.0, offset=0.0)
centimeter = Unit(name="centimeter", symbol="cm", dimension=LENGTH, scale_factor=0.01, offset=0.0)
celsius = Unit(name="celsius", symbol="°C", dimension=TEMPERATURE, scale_factor=1.0, offset=0.0)
kilogram = Unit(name="kilogram", symbol="kg", dimension=MASS, scale_factor=1.0, offset=0.0)
second = Unit(name="second", symbol="s", dimension=TIME, scale_factor=1.0, offset=0.0)
ampere = Unit(name="ampere", symbol="A", dimension=CURRENT, scale_factor=1.0, offset=0.0)
kelvin = Unit(name="kelvin", symbol="K", dimension=TEMPERATURE, scale_factor=1.0, offset=273.15)
mole = Unit(name="mole", symbol="mol", dimension=AMOUNT, scale_factor=1.0, offset=0.0)
candela = Unit(name="candela", symbol="cd", dimension=LUMINOUS_INTENSITY, scale_factor=1.0, offset=0.0)


def convert_unit(value: float, source: Unit, target: Unit) -> float:
    """Convert a scalar value between compatible units.

    The implementation supports scale-based conversions for linear units such as
    meter <-> centimeter and offset-based conversions for temperature units
    such as Celsius <-> Kelvin.
    """

    if source.dimension != target.dimension:
        raise ValueError("Cannot convert between different dimensions")

    if source == target:
        return value

    base_value = (value - source.offset) * source.scale_factor
    return target.offset + (base_value / target.scale_factor)
