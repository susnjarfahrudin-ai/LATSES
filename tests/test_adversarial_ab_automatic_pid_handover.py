"""Automatic A/B adversarial rotation over isolated OS processes.

This is a test-only acceptance harness. The parent process injects attacks, but
it never commands TAKEOVER or RECOVER. Each role observes its own failure,
sends only verified AdaptiveDefense evidence to its peer, and the peer
promotes itself automatically. The recovering process becomes READY from the
peer's recovery signal. No peer runtime/model state is transferred.
"""

from __future__ import annotations

import multiprocessing as mp
import os
from pathlib import Path
import time

from lat_ces.security.adaptive_defense import AdaptiveDefense, DefenseRecord
from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
    ROMCoordinator,
)

_TIMEOUT = 15.0


def _recv(conn: mp.connection.Connection) -> dict:
    deadline = time.monotonic() + _TIMEOUT
    while time.monotonic() < deadline:
        if conn.poll(0.1):
            return conn.recv()
    raise AssertionError("timed out waiting for isolated role process")


def _runtime(
    role: ExecutionRole,
    control_in: mp.connection.Connection,
    event_out: mp.connection.Connection,
    peer_in: mp.connection.Connection,
    peer_out: mp.connection.Connection,
    state_dir: str,
) -> None:
    pid = os.getpid()
    root = Path(state_dir)
    root.mkdir(parents=True, exist_ok=False)
    defense = AdaptiveDefense()

    baseline = RecoveryCheckpoint(
        "baseline-001",
        "sha256:last-known-good",
        f"verification/{role.value}/baseline-001",
    )
    if role is ExecutionRole.PROCESS:
        machine = RecoveryStateMachine(active_role=role, checkpoint=baseline)
    else:
        machine = RecoveryStateMachine(
            state=RecoveryState.STANDBY,
            active_role=ExecutionRole.PROCESS,
            recovering_role=role,
            checkpoint=baseline,
        )

    event_out.send(
        {"event": "READY", "role": role.value, "pid": pid, "state": machine.state.value}
    )

    while True:
        # Parent commands and peer handover/recovery signals are both observed
        # by the worker; takeover/recovery is never issued by the parent.
        if peer_in.poll(0.05):
            message = peer_in.recv()
        elif control_in.poll(0.05):
            message = control_in.recv()
        else:
            continue
        command = message["command"]

        if command == "ATTACK":
            if machine.active_role is not role:
                event_out.send(
                    {"event": "REJECTED_ATTACK", "role": role.value, "pid": pid}
                )
                continue

            health = HealthState[message["health"]]
            machine = machine.on_failure(health)
            observed = defense.observe_failure(
                message["invariant_id"],
                message["attack_class"],
                message["evidence"],
                source=role.value,
            )
            defense.quarantine(observed)
            verified = defense.promote(
                observed,
                verification_sha=message["verification_sha"],
            )
            signal = ROMCoordinator(role, baseline).observe_failure(health)

            (root / "attack.json").write_text(
                "attack=" + message["attack_id"] + "\n"
                + "pid=" + str(pid) + "\n"
                + "record=" + verified.digest + "\n",
                encoding="utf-8",
            )

            # Only immutable, verified defense evidence crosses the A/B
            # boundary. Runtime/model state is explicitly absent.
            peer_out.send(
                {
                    "command": "HANDOVER",
                    "from_role": role.value,
                    "recipient_role": signal.recipient_role.value,
                    "cause": signal.cause.value,
                    "checkpoint_revision": signal.checkpoint.revision_id,
                    "checkpoint_hash": signal.checkpoint.content_hash,
                    "provenance": signal.provenance,
                    "record": verified,
                    "peer_runtime": None,
                }
            )
            event_out.send(
                {
                    "event": "FAILURE",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "recipient": signal.recipient_role.value,
                    "attack_id": message["attack_id"],
                    "verified": verified.verified,
                }
            )
            continue

        if command == "HANDOVER":
            if message["recipient_role"] != role.value:
                raise AssertionError("handover delivered to the wrong role")
            record = message["record"]
            if not isinstance(record, DefenseRecord):
                raise AssertionError("handover must carry a DefenseRecord")
            if not record.verified or not record.verification_sha:
                raise AssertionError("unverified defense crossed the A/B boundary")
            defense.import_verified(record)
            if machine.state is not RecoveryState.STANDBY:
                raise AssertionError(f"automatic takeover requires STANDBY, got {machine.state}")
            machine = machine.promote_standby()

            checkpoint = RecoveryCheckpoint(
                message["checkpoint_revision"],
                message["checkpoint_hash"],
                message["provenance"],
            )
            event_out.send(
                {
                    "event": "TAKEOVER",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "active_role": machine.active_role.value,
                    "recovering_role": machine.recovering_role.value,
                    "source_role": message["from_role"],
                    "peer_runtime_transferred": message["peer_runtime"] is not None,
                    "record_imported": any(r.digest == record.digest for r in defense.records()),
                }
            )

            # Automatic recovery signal back to the isolated source role.
            peer_out.send(
                {
                    "command": "RECOVER",
                    "checkpoint_revision": f"{role.value}-recovery-from-{record.invariant_id}",
                    "verification_sha": record.verification_sha,
                    "provenance": f"verification/{role.value}/recovery",
                }
            )
            continue

        if command == "RECOVER":
            checkpoint = RecoveryCheckpoint(
                message["checkpoint_revision"],
                message["verification_sha"],
                message["provenance"],
            )
            if machine.state is not RecoveryState.TAKEOVER:
                raise AssertionError(f"automatic recovery requires TAKEOVER, got {machine.state}")
            machine = machine.activate_standby().promote_standby()
            machine = machine.begin_recovery(checkpoint).verify_checkpoint().mark_ready()
            (root / "recovery.json").write_text(
                "checkpoint=" + checkpoint.revision_id + "\n"
                + "pid=" + str(pid) + "\n",
                encoding="utf-8",
            )
            event_out.send(
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
            event_out.send(
                {
                    "event": "SNAPSHOT",
                    "role": role.value,
                    "pid": pid,
                    "state": machine.state.value,
                    "active_role": machine.active_role.value,
                    "recovering_role": machine.recovering_role.value if machine.recovering_role else None,
                    "state_files": sorted(p.name for p in root.iterdir()),
                    "defense_records": [r.digest for r in defense.records()],
                }
            )
            continue

        if command == "STOP":
            event_out.send({"event": "STOPPED", "role": role.value, "pid": pid})
            return

        raise AssertionError(f"unknown command: {command}")


def test_automatic_bidirectional_a_b_pid_handover_rotation(tmp_path: Path) -> None:
    """Attack A -> automatic B takeover -> automatic A recovery -> reverse."""
    ctx = mp.get_context("spawn")
    a_control_in, a_control_send = ctx.Pipe(duplex=False)
    a_event_recv, a_event_out = ctx.Pipe(duplex=False)
    b_control_in, b_control_send = ctx.Pipe(duplex=False)
    b_event_recv, b_event_out = ctx.Pipe(duplex=False)
    a_to_b_out, a_to_b_in = ctx.Pipe(duplex=False)
    b_to_a_out, b_to_a_in = ctx.Pipe(duplex=False)
    a_dir = tmp_path / "A"
    b_dir = tmp_path / "B"

    a = ctx.Process(
        target=_runtime,
        args=(
            ExecutionRole.PROCESS,
            a_control_in,
            a_event_out,
            b_to_a_in,
            a_to_b_out,
            str(a_dir),
        ),
        name="LATCES-A",
    )
    b = ctx.Process(
        target=_runtime,
        args=(
            ExecutionRole.REVISION_RECOVERY,
            b_control_in,
            b_event_out,
            a_to_b_in,
            b_to_a_out,
            str(b_dir),
        ),
        name="LATCES-B",
    )
    a.start()
    b.start()

    try:
        ready_a = _recv(a_event_recv)
        ready_b = _recv(b_event_recv)
        assert ready_a["pid"] == a.pid
        assert ready_b["pid"] == b.pid
        assert a.pid != b.pid
        assert ready_a["state"] == RecoveryState.ACTIVE.value
        assert ready_b["state"] == RecoveryState.STANDBY.value

        # Round 1: inject attack into A. Parent sends ATTACK only.
        a_control_send.send(
            {
                "command": "ATTACK",
                "attack_id": "attack-A-001",
                "attack_class": "ipc/replay-capacity",
                "invariant_id": "A-attack-001",
                "evidence": "A observed replay-capacity degradation",
                "health": "DEGRADED",
                "verification_sha": "sha256:defense-A-001",
            }
        )
        failure_a = _recv(a_event_recv)
        takeover_b = _recv(b_event_recv)
        assert failure_a["event"] == "FAILURE"
        assert failure_a["pid"] == a.pid
        assert failure_a["verified"] is True
        assert failure_a["recipient"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_b["event"] == "TAKEOVER"
        assert takeover_b["pid"] == b.pid
        assert takeover_b["active_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_b["source_role"] == ExecutionRole.PROCESS.value
        assert takeover_b["peer_runtime_transferred"] is False
        assert takeover_b["record_imported"] is True

        recovered_a = _recv(a_event_recv)
        assert recovered_a["event"] == "RECOVERED"
        assert recovered_a["pid"] == a.pid
        assert recovered_a["state"] == RecoveryState.READY.value
        assert recovered_a["active_role"] == ExecutionRole.REVISION_RECOVERY.value

        # Round 2: inject attack into B. Parent sends ATTACK only again.
        b_control_send.send(
            {
                "command": "ATTACK",
                "attack_id": "attack-B-001",
                "attack_class": "flowguard/4d-pressure",
                "invariant_id": "B-attack-001",
                "evidence": "B observed simultaneous limiter pressure",
                "health": "UNAVAILABLE",
                "verification_sha": "sha256:defense-B-001",
            }
        )
        failure_b = _recv(b_event_recv)
        takeover_a = _recv(a_event_recv)
        assert failure_b["event"] == "FAILURE"
        assert failure_b["pid"] == b.pid
        assert failure_b["verified"] is True
        assert failure_b["recipient"] == ExecutionRole.PROCESS.value
        assert takeover_a["event"] == "TAKEOVER"
        assert takeover_a["pid"] == a.pid
        assert takeover_a["active_role"] == ExecutionRole.PROCESS.value
        assert takeover_a["source_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_a["peer_runtime_transferred"] is False
        assert takeover_a["record_imported"] is True

        recovered_b = _recv(b_event_recv)
        assert recovered_b["event"] == "RECOVERED"
        assert recovered_b["pid"] == b.pid
        assert recovered_b["state"] == RecoveryState.READY.value
        assert recovered_b["active_role"] == ExecutionRole.PROCESS.value

        # Both original OS processes survived the complete rotation.
        assert a.is_alive()
        assert b.is_alive()
        assert a.pid != b.pid

        a_control_send.send({"command": "SNAPSHOT"})
        final_a = _recv(a_event_recv)
        b_control_send.send({"command": "SNAPSHOT"})
        final_b = _recv(b_event_recv)
        assert final_a["pid"] == a.pid
        assert final_b["pid"] == b.pid
        assert final_a["active_role"] == ExecutionRole.PROCESS.value
        assert final_b["active_role"] == ExecutionRole.PROCESS.value
        assert "attack.json" in final_a["state_files"]
        assert "recovery.json" in final_a["state_files"]
        assert "attack.json" in final_b["state_files"]
        assert "recovery.json" in final_b["state_files"]
    finally:
        for sender, receiver in (
            (a_control_send, a_event_recv),
            (b_control_send, b_event_recv),
        ):
            try:
                sender.send({"command": "STOP"})
                _recv(receiver)
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
