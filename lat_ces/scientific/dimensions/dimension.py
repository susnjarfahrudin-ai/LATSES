from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Dimension:
    """Canonical SI base-dimension exponent vector."""

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
            for value in (self.L, self.M, self.T, self.I, self.Theta, self.N, self.J)
        )


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
AREA = LENGTH**2
FLOW_RATE = (LENGTH**3) / TIME
MASS_FLOW = MASS / TIME
PRESSURE = MASS / (LENGTH * (TIME**2))
POWER = (MASS * (LENGTH**2)) / (TIME**3)
SPECIFIC_HEAT = (LENGTH**2) / (TIME**2) / TEMPERATURE
HEAT_RATE = POWER
DYNAMIC_VISCOSITY = MASS / (LENGTH * TIME)

__all__ = [name for name in globals() if not name.startswith("_")]