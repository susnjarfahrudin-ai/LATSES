# LAT-SEC-001 — Security Hardening Architecture

## Security boundary

```text
                 Canonical LAT-CES state
                         │
                         ▼
                Security Boundary Layer
        ┌────────────┬─────────────┬──────────────┐
        │ Root of    │ Process     │ Signed IPC   │
        │ Trust      │ Identity    │ + Replay     │
        │ + KeyRing  │ + Isolation │ Guard        │
        └────────────┴─────────────┴──────────────┘
                         │
                         ▼
                 Crash-safe persistence
                         │
                         ▼
                  Threat scoring
```

## Invariants

1. Root secrets are obtained through an OS keyring abstraction; there is no plaintext `.key` file fallback.
2. Root keys are versioned. Application subkeys are derived with HKDF-SHA256 using an explicit purpose (`info`) value.
3. Sensitive values are exposed through mutable buffers where possible and are explicitly zeroed after use.
4. Persistent replacement follows write → flush/fsync → atomic replace. POSIX also fsyncs the containing directory after the rename.
5. Linux startup hardening disables the dumpable flag and attempts to set the core-dump resource limit to zero. Windows uses supported process mitigation policies for dynamic-code and extension-point restrictions.
6. Process identity is `(pid, kernel start token)` plus a fresh UUID and UTC creation timestamp. PID alone is never an identity proof.
7. IPC authentication is HMAC-SHA256 over a canonical envelope containing protocol version, sender identity, nonce, timestamp, and payload. The receiver tracks nonces and enforces freshness, so nonce generation alone is not treated as replay protection.
8. Threat scoring is per IP address with time decay. Configured CIDR allowlists are never blocked by the local scorer.
9. The security layer does not claim protection against a privileged kernel attacker, a compromised OS keyring, or physical RAM acquisition after power loss.

## Integration order

```text
security primitives
      ↓
constitutional key registry integration
      ↓
Consul / station IPC migration
      ↓
persistent state migration to atomic writer
      ↓
startup process isolation
      ↓
threat-score enforcement
```

The first implementation is intentionally additive. Existing engineering models and GUI state are not modified by this foundation layer.
