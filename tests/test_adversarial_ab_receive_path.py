"""Adversarial proof that A/B takeover is triggered by the peer receive path.

This test deliberately separates two claims:
1. Module B's state machine can promote itself when directly invoked (capability).
2. In the isolated production-like path, the parent never invokes B's takeover;
   B becomes active only after receiving A's verified HANDOVER message.

Test-only. No production security or Module A/B code is changed.
"""

from __future__ import annotations

import multiprocessing as mp
from pathlib import Path

from lat_ces.security.adaptive_defense import AdaptiveDefense
from lat_ces.structural.role_handover import (
    ExecutionRole,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
)

from tests.test_adversarial_ab_automatic_pid_handover import _recv, _runtime


def test_b_direct_capability_is_distinct_from_actual_receive_path(tmp_path: Path) -> None:
    """Direct B promotion proves capability; A->B receive proves the trigger path."""
    baseline = RecoveryCheckpoint(
        "baseline-proof-001",
        "sha256:last-known-good",
        "verification/receive-path/baseline-001",
    )

    # Capability-only proof: B can promote when explicitly invoked in isolation.
    direct = RecoveryStateMachine(
        state=RecoveryState.STANDBY,
        active_role=ExecutionRole.PROCESS,
        recovering_role=ExecutionRole.REVISION_RECOVERY,
        checkpoint=baseline,
    )
    promoted = direct.promote_standby()
    assert promoted.active_role is ExecutionRole.REVISION_RECOVERY

    # Trigger-path proof: parent sends an ATTACK only to A. B is never given a
    # takeover command; its only takeover input is A's peer HANDOVER message.
    ctx = mp.get_context("spawn")
    a_control_in, a_control_send = ctx.Pipe(duplex=False)
    a_event_recv, a_event_out = ctx.Pipe(duplex=False)
    b_control_in, b_control_send = ctx.Pipe(duplex=False)
    b_event_recv, b_event_out = ctx.Pipe(duplex=False)
    a_to_b_recv, a_to_b_send = ctx.Pipe(duplex=False)
    b_to_a_recv, b_to_a_send = ctx.Pipe(duplex=False)
    a_dir = tmp_path / "A"
    b_dir = tmp_path / "B"

    a = ctx.Process(
        target=_runtime,
        args=(ExecutionRole.PROCESS, a_control_in, a_event_out, b_to_a_recv, a_to_b_send, str(a_dir)),
        name="LATCES-A-receive-proof",
    )
    b = ctx.Process(
        target=_runtime,
        args=(
            ExecutionRole.REVISION_RECOVERY,
            b_control_in,
            b_event_out,
            a_to_b_recv,
            b_to_a_send,
            str(b_dir),
        ),
        name="LATCES-B-receive-proof",
    )
    a.start()
    b.start()

    try:
        ready_a = _recv(a_event_recv)
        ready_b = _recv(b_event_recv)
        assert ready_a["state"] == RecoveryState.ACTIVE.value
        assert ready_b["state"] == RecoveryState.STANDBY.value

        # Directly attacking B while it is standby must not activate B.
        b_control_send.send(
            {
                "command": "ATTACK",
                "attack_id": "direct-B-attack",
                "attack_class": "adversarial/direct-trigger",
                "invariant_id": "B-direct-001",
                "evidence": "direct parent input to standby B",
                "health": "DEGRADED",
                "verification_sha": "sha256:direct-B",
            }
        )
        rejected = _recv(b_event_recv)
        assert rejected["event"] == "REJECTED_ATTACK"
        assert rejected["pid"] == b.pid

        # The only trigger now is A's real failure -> peer HANDOVER -> B receive.
        a_control_send.send(
            {
                "command": "ATTACK",
                "attack_id": "receive-path-A-001",
                "attack_class": "ipc/replay-capacity",
                "invariant_id": "A-receive-001",
                "evidence": "A observed replay-capacity degradation",
                "health": "DEGRADED",
                "verification_sha": "sha256:receive-path-A",
            }
        )
        failure_a = _recv(a_event_recv)
        takeover_b = _recv(b_event_recv)

        assert failure_a["event"] == "FAILURE"
        assert failure_a["recipient"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_b["event"] == "TAKEOVER"
        assert takeover_b["pid"] == b.pid
        assert takeover_b["source_role"] == ExecutionRole.PROCESS.value
        assert takeover_b["active_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_b["peer_runtime_transferred"] is False
        assert takeover_b["record_imported"] is True
    finally:
        for sender, receiver in ((a_control_send, a_event_recv), (b_control_send, b_event_recv)):
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
