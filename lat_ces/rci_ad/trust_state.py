"""Canonical trust states; trust is independent from integrity."""
from enum import Enum


class TrustState(str, Enum):
    UNTRUSTED = "UNTRUSTED"
    TRUSTED = "TRUSTED"
    REVOKED = "REVOKED"
