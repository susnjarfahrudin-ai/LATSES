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
        return canonical_dimension(
            L=self.L + other.L,
            M=self.M + other.M,
            T=self.T + other.T,
            I=self.I + other.I,
            Theta=self.Theta + other.Theta,
            N=self.N + other.N,
            J=self.J + other.J,
        )

    def __truediv__(self, other: "Dimension") -> "Dimension":
        return canonical_dimension(
            L=self.L - other.L,
            M=self.M - other.M,
            T=self.T - other.T,
            I=self.I - other.I,
            Theta=self.Theta - other.Theta,
            N=self.N - other.N,
            J=self.J - other.J,
        )

    def __pow__(self, power: int | float) -> "Dimension":
        return canonical_dimension(
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


_DIMENSION_CACHE: dict[tuple[int, int, int, int, int, int, int], Dimension] = {}


def canonical_dimension(
    *,
    L: int = 0,
    M: int = 0,
    T: int = 0,
    I: int = 0,
    Theta: int = 0,
    N: int = 0,
    J: int = 0,
) -> Dimension:
    """Return the unique Dimension instance for an exponent vector."""
    key = (int(L), int(M), int(T), int(I), int(Theta), int(N), int(J))
    dimension = _DIMENSION_CACHE.get(key)
    if dimension is None:
        dimension = Dimension(*key)
        _DIMENSION_CACHE[key] = dimension
    return dimension


DIMENSIONLESS = canonical_dimension()
LENGTH = canonical_dimension(L=1)
MASS = canonical_dimension(M=1)
TIME = canonical_dimension(T=1)
CURRENT = canonical_dimension(I=1)
TEMPERATURE = canonical_dimension(Theta=1)
AMOUNT = canonical_dimension(N=1)
LUMINOUS_INTENSITY = canonical_dimension(J=1)
VELOCITY = canonical_dimension(L=1, T=-1)
DENSITY = canonical_dimension(M=1, L=-3)
ACCELERATION = canonical_dimension(L=1, T=-2)
FORCE = canonical_dimension(M=1, L=1, T=-2)
AREA = canonical_dimension(L=2)
FLOW_RATE = canonical_dimension(L=3, T=-1)
MASS_FLOW = canonical_dimension(M=1, T=-1)
PRESSURE = canonical_dimension(M=1, L=-1, T=-2)
POWER = canonical_dimension(M=1, L=2, T=-3)
SPECIFIC_HEAT = canonical_dimension(L=2, T=-2, Theta=-1)
HEAT_RATE = POWER
DYNAMIC_VISCOSITY = canonical_dimension(M=1, L=-1, T=-1)

__all__ = [name for name in globals() if not name.startswith("_")]
