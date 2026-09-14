"""Runtime-process A/B adversarial acceptance test.

This is deliberately a test-only harness. It proves OS-process separation,
separate state directories, one-way evidence transfer, takeover, recovery,
and the reverse rotation. It does not copy peer runtime/model state.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
from pathlib import Path
import time

from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
    ROMCoordinator,
)


_TIMEOUT = 15.0


def _runtime(
    role: ExecutionRole,
    state_dir: str,
    control: mp.connection.Connection,
) -> None:
    """Run one isolated role in its own OS process and state directory."""
    pid = os.getpid()
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=False)

    baseline = RecoveryCheckpoint(
        "baseline-001",
        "sha256:last-known-good",
        f"verification/{role.value}/baseline-001",
    )
    if role is ExecutionRole.PROCESS:
        machine = RecoveryStateMachine(active_role=role, checkpoint=baseline)
    else:
        # B starts as the standby role while A is active.
        machine = RecoveryStateMachine(
            state=RecoveryState.STANDBY,
            active_role=ExecutionRole.PROCESS,
            recovering_role=role,
            checkpoint=baseline,
        )

    (root / "identity.json").write_text(
        json.dumps({"role": role.value, "pid": pid, "state": machine.state.value}),
        encoding="utf-8",
    )
    control.send({"event": "READY", "role": role.value, "pid": pid, "state": machine.state.value})

    while True:
        message = control.recv()
        command = message["command"]

        if command == "ATTACK":
            if machine.active_role is not role:
                control.send({"event": "REJECTED_ATTACK", "role": role.value, "pid": pid})
                continue
            health = HealthState[message["health"]]
            transition = machine.on_failure(health)
            signal = ROMCoordinator(role, machine.checkpoint).observe_failure(health)
            machine = transition
            (root / "attack.json").write_text(
                json.dumps(
                    {
                        "attack_id": message["attack_id"],
                        "attack_path": message["attack_path"],
                        "pid": pid,
                    }
                ),
                encoding="utf-8",
            )
            control.send(
                {
                    "event": "FAILURE",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "recipient": signal.recipient_role.value,
                    "checkpoint": signal.checkpoint.revision_id,
                    "attack_id": message["attack_id"],
                }
            )
            continue

        if command == "TAKEOVER":
            checkpoint = RecoveryCheckpoint(
                message["checkpoint_revision"],
                message["verification_sha"],
                message["provenance"],
            )
            if machine.state is RecoveryState.STANDBY:
                machine = machine.promote_standby()
            elif machine.state is RecoveryState.READY:
                machine = machine.on_failure(HealthState.UNAVAILABLE).activate_standby().promote_standby()
            else:
                raise AssertionError(f"takeover not legal from {machine.state}")
            control.send(
                {
                    "event": "TAKEOVER",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "active_role": machine.active_role.value,
                    "recovering_role": machine.recovering_role.value,
                    "checkpoint": checkpoint.revision_id,
                    "has_peer_runtime": "peer_runtime" in message,
                }
            )
            continue

        if command == "RECOVER":
            checkpoint = RecoveryCheckpoint(
                message["checkpoint_revision"],
                message["verification_sha"],
                message["provenance"],
            )
            if machine.state is RecoveryState.TAKEOVER:
                machine = machine.activate_standby().promote_standby()
            machine = machine.begin_recovery(checkpoint).verify_checkpoint().mark_ready()
            (root / "recovery.json").write_text(
                json.dumps(
                    {
                        "checkpoint": checkpoint.revision_id,
                        "verification_sha": checkpoint.content_hash,
                        "pid": pid,
                    }
                ),
                encoding="utf-8",
            )
            control.send(
                {
                    "event": "RECOVERED",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "active_role": machine.active_role.value,
                    "recovering_role": machine.recovering_role.value,
                }
            )
            continue

        if command == "SNAPSHOT":
            control.send(
                {
                    "event": "SNAPSHOT",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "active_role": machine.active_role.value,
                    "recovering_role": (
                        machine.recovering_role.value if machine.recovering_role is not None else None
                    ),
                    "state_files": sorted(p.name for p in root.iterdir()),
                }
            )
            continue

        if command == "STOP":
            control.send({"event": "STOPPED", "role": role.value, "pid": pid})
            return

        raise AssertionError(f"unknown command: {command}")


def _recv(conn: mp.connection.Connection) -> dict:
    deadline = time.monotonic() + _TIMEOUT
    while time.monotonic() < deadline:
        if conn.poll(0.1):
            return conn.recv()
    raise AssertionError("timed out waiting for isolated role process")


def test_real_pid_ab_isolation_bidirectional_role_rotation(tmp_path: Path) -> None:
    """Attack A -> B takeover -> A recovery -> attack B -> A takeover."""
    ctx = mp.get_context("spawn")
    a_parent, a_child = ctx.Pipe()
    b_parent, b_child = ctx.Pipe()
    a_dir = tmp_path / "A"
    b_dir = tmp_path / "B"

    a = ctx.Process(
        target=_runtime,
        args=(ExecutionRole.PROCESS, str(a_dir), a_child),
        name="LATCES-A",
    )
    b = ctx.Process(
        target=_runtime,
        args=(ExecutionRole.REVISION_RECOVERY, str(b_dir), b_child),
        name="LATCES-B",
    )
    a.start()
    b.start()

    try:
        ready_a = _recv(a_parent)
        ready_b = _recv(b_parent)
        assert ready_a["role"] == ExecutionRole.PROCESS.value
        assert ready_b["role"] == ExecutionRole.REVISION_RECOVERY.value
        assert ready_a["pid"] == a.pid
        assert ready_b["pid"] == b.pid
        assert a.pid != b.pid
        assert ready_a["pid"] != ready_b["pid"]
        assert a_dir != b_dir
        assert ready_a["state"] == RecoveryState.ACTIVE.value
        assert ready_b["state"] == RecoveryState.STANDBY.value

        # Round 1: attack A only.
        a_parent.send(
            {
                "command": "ATTACK",
                "attack_id": "attack-A-001",
                "attack_path": "ipc/replay-capacity",
                "health": "DEGRADED",
            }
        )
        failure_a = _recv(a_parent)
        assert failure_a["event"] == "FAILURE"
        assert failure_a["pid"] == a.pid
        assert failure_a["recipient"] == ExecutionRole.REVISION_RECOVERY.value
        assert failure_a["checkpoint"] == "baseline-001"

        # B must not be affected merely because A was attacked.
        b_parent.send({"command": "SNAPSHOT"})
        b_before = _recv(b_parent)
        assert b_before["pid"] == b.pid
        assert b_before["state"] == RecoveryState.STANDBY.value
        assert b_before["active_role"] == ExecutionRole.PROCESS.value
        assert "attack.json" not in b_before["state_files"]

        # Verified evidence only crosses the boundary; peer runtime is forbidden.
        b_parent.send(
            {
                "command": "TAKEOVER",
                "checkpoint_revision": "B-prepared-A-001",
                "verification_sha": "sha256:defense-A-001",
                "provenance": "verification/B-prepared-A-001",
            }
        )
        takeover_b = _recv(b_parent)
        assert takeover_b["event"] == "TAKEOVER"
        assert takeover_b["pid"] == b.pid
        assert takeover_b["active_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_b["recovering_role"] == ExecutionRole.PROCESS.value
        assert takeover_b["has_peer_runtime"] is False

        a_parent.send(
            {
                "command": "RECOVER",
                "checkpoint_revision": "A-recovery-from-verified-defense",
                "verification_sha": "sha256:defense-A-001",
                "provenance": "verification/A-recovery-from-verified-defense",
            }
        )
        recovered_a = _recv(a_parent)
        assert recovered_a["event"] == "RECOVERED"
        assert recovered_a["pid"] == a.pid
        assert recovered_a["state"] == RecoveryState.READY.value
        assert recovered_a["active_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert recovered_a["recovering_role"] == ExecutionRole.PROCESS.value

        # Round 2: attack B only.
        b_parent.send(
            {
                "command": "ATTACK",
                "attack_id": "attack-B-001",
                "attack_path": "flowguard/frequency-volume-concurrency-novelty",
                "health": "UNAVAILABLE",
            }
        )
        failure_b = _recv(b_parent)
        assert failure_b["event"] == "FAILURE"
        assert failure_b["pid"] == b.pid
        assert failure_b["recipient"] == ExecutionRole.PROCESS.value

        # A is now the takeover target and must remain a distinct PID.
        a_parent.send(
            {
                "command": "TAKEOVER",
                "checkpoint_revision": "A-prepared-B-001",
                "verification_sha": "sha256:defense-B-001",
                "provenance": "verification/A-prepared-B-001",
            }
        )
        takeover_a = _recv(a_parent)
        assert takeover_a["event"] == "TAKEOVER"
        assert takeover_a["pid"] == a.pid
        assert takeover_a["active_role"] == ExecutionRole.PROCESS.value
        assert takeover_a["recovering_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_a["has_peer_runtime"] is False

        b_parent.send(
            {
                "command": "RECOVER",
                "checkpoint_revision": "B-recovery-from-verified-defense",
                "verification_sha": "sha256:defense-B-001",
                "provenance": "verification/B-recovery-from-verified-defense",
            }
        )
        recovered_b = _recv(b_parent)
        assert recovered_b["event"] == "RECOVERED"
        assert recovered_b["pid"] == b.pid
        assert recovered_b["state"] == RecoveryState.READY.value
        assert recovered_b["active_role"] == ExecutionRole.PROCESS.value
        assert recovered_b["recovering_role"] == ExecutionRole.REVISION_RECOVERY.value

        # Final invariant: both OS processes remained alive and distinct throughout.
        assert a.is_alive()
        assert b.is_alive()
        assert a.pid != b.pid
    finally:
        for conn in (a_parent, b_parent):
            try:
                conn.send({"command": "STOP"})
                _recv(conn)
            except (BrokenPipeError, EOFError, AssertionError):
                pass
        a.join(timeout=5)
        b.join(timeout=5)
        if a.is_alive():
            a.terminate()
            a.join(timeout=2)
        if b.is_alive():
            b.terminate()
            b.join(timeout=2)

        assert a.exitcode == 0, f"A process exitcode={a.exitcode}"
        assert b.exitcode == 0, f"B process exitcode={b.exitcode}"
