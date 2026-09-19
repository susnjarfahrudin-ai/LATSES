"""Canonical integrity states; integrity is independent from trust."""
from enum import Enum


class IntegrityState(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    MODIFIED = "MODIFIED"
    COMPROMISED = "COMPROMISED"
