"""
LAT-CES Core: Constitutional Axioms (CAX)
Dokumenti: LAT-CES-0001 do LAT-CES-0003
"""

from dataclasses import dataclass
from enum import Enum


class AuthorityLevel(Enum):
    """Structural constitutional ordering, not epistemic evidence authority."""

    PHYSICAL_REALITY = 1
    MATHEMATICAL_MODEL = 2
    SOFTWARE_ENGINE = 3
    AI_ASSISTANT = 4


@dataclass(frozen=True)
class Axiom:
    """A minimal immutable constitutional axiom representation."""

    name: str
    statement: str


class ConstitutionalAxiom:
    """Core constitutional axiom helpers and authority rules."""

    AXIOM_1_REALITY_SUPREMACY = (
        "Fizička realnost je krajnji referent. Mjerenja su dokazni podaci o realnosti "
        "i podliježu provjeri; nijedno mjerenje, model, softver ili AI rezultat "
        "nema samostalni autoritet da proglasi naučnu istinu."
    )
    AXIOM_7_TRACEABILITY = (
        "Svaka inženjerska odluka i objekt mora imati potpuni kriptografski dokaz porijekla."
    )

    @staticmethod
    def validate_authority(higher: AuthorityLevel, lower: AuthorityLevel) -> bool:
        """Ensure structural constitutional precedence is not reversed.

        This is not an epistemic verification mechanism and does not promote
        data or measurements to VERIFIED evidence.
        """
        return higher.value < lower.value


class ConstitutionalAxioms:
    """Static collection of foundational axioms."""

    @staticmethod
    def all() -> list[Axiom]:
        return [
            Axiom("identity", "A system is itself."),
            Axiom("consistency", "A system should not contradict itself."),
            Axiom("reality_supremacy", ConstitutionalAxiom.AXIOM_1_REALITY_SUPREMACY),
            Axiom("traceability", ConstitutionalAxiom.AXIOM_7_TRACEABILITY),
        ]
