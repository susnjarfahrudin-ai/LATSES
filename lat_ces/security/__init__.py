"""Security-hardening primitives for the LAT-CES runtime boundary."""

from .secure_memory import secure_zero
from .atomic_persistence import atomic_write_bytes
from .keyring import KeyRing, SecretStore, hkdf_sha256
from .process_security import ProcessIdentity, ProcessIsolationResult, activate_process_isolation, current_process_identity, is_process_alive
from .secure_ipc import ReplayGuard, SecurityError, SignedIPCChannel
from .threat_score import ThreatScoreEngine, ThreatScorePolicy

__all__ = [
    "KeyRing", "ProcessIdentity", "ProcessIsolationResult", "ReplayGuard",
    "SecurityError", "SecretStore", "SignedIPCChannel", "ThreatScoreEngine",
    "ThreatScorePolicy", "activate_process_isolation", "atomic_write_bytes",
    "current_process_identity", "hkdf_sha256", "is_process_alive", "secure_zero",
]
