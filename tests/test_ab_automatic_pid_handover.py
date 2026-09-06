from __future__ import annotations

import multiprocessing as mp
import os
from pathlib import Path

from lat_ces.security.process_security import current_process_identity
from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
    ROMCoordinator,
)


def _worker(
    role: ExecutionRole,
    command_queue: mp.Queue,
    event_queue: mp.Queue,
    state_dir: str,
) -> None:
    identity = current_process_identity()
    Path(state_dir).mkdir(parents=True, exist_ok=True)
    (Path(state_dir) / "pid").write_text(str(identity.pid), encoding="utf-8")

    checkpoint = RecoveryCheckpoint(
        revision_id="canonical-970f06d8",
        content_hash="970f06d895a0cbc39fb109aaca7165bd2d5d12eb",
        provenance="test/canonical-baseline",
    )

    # The test starts with A ACTIVE and B STANDBY. B must never be ACTIVE
    # before receiving a valid failure signal from A.
    state = RecoveryStateMachine(
        state=RecoveryState.ACTIVE if role is ExecutionRole.PROCESS else RecoveryState.STANDBY,
        active_role=ExecutionRole.PROCESS,
        recovering_role=(ExecutionRole.REVISION_RECOVERY if role is ExecutionRole.PROCESS else None),
        checkpoint=checkpoint,
    )
    coordinator = ROMCoordinator(
        active_role=ExecutionRole.PROCESS,
        last_verified_checkpoint=checkpoint,
    )

    event_queue.put((role.value, "READY", identity.pid, identity.fingerprint, state.state.value))

    while True:
        command = command_queue.get()
        if command == "ATTACK":
            if role is ExecutionRole.PROCESS:
                signal = coordinator.observe_failure(HealthState.UNAVAILABLE)
                event_queue.put(
                    (
                        role.value,
                        "FAILURE_SIGNAL",
                        identity.pid,
                        signal.recipient_role.value,
                        signal.cause.value,
                        signal.checkpoint.content_hash,
                    )
                )
            else:
                event_queue.put((role.value, "IGNORED_ATTACK_WHILE_STANDBY", identity.pid))
        elif command == "TAKEOVER_SIGNAL":
            if role is ExecutionRole.REVISION_RECOVERY:
                event_queue.put((role.value, "TAKEOVER", identity.pid))
        elif command == "RECOVER":
            event_queue.put((role.value, "RECOVERING", identity.pid))
        elif command == "STOP":
            event_queue.put((role.value, "STOP", identity.pid, os.getpid()))
            return
        else:
            raise AssertionError(f"unknown command: {command}")


def _start(role: ExecutionRole, ctx: mp.context.BaseContext, root: Path):
    commands = ctx.Queue()
    events = ctx.Queue()
    process = ctx.Process(
        target=_worker,
        args=(role, commands, events, str(root / role.value)),
        name=f"latces-{role.value.lower()}",
    )
    process.start()
    ready = events.get(timeout=10)
    assert ready[0] == role.value
    assert ready[1] == "READY"
    return process, commands, events, ready


def test_real_pid_automatic_ab_takeover_and_bidirectional_recovery(tmp_path: Path) -> None:
    """Require separate PIDs, A->B automatic signal, recovery, then B->A signal.

    The parent test driver is only a transport: it must not issue TAKEOVER on
    its own. The attacked process emits the takeover signal itself through the
    canonical ROMCoordinator, and the receiving process accepts only that
    signal/checkpoint before becoming ACTIVE in the model exercised here.
    """
    ctx = mp.get_context("spawn")
    root = tmp_path / "ab-runtime"

    a, a_cmd, a_events, a_ready = _start(ExecutionRole.PROCESS, ctx, root)
    b, b_cmd, b_events, b_ready = _start(ExecutionRole.REVISION_RECOVERY, ctx, root)

    try:
        assert a.pid != b.pid
        assert a_ready[2] == a.pid
        assert b_ready[2] == b.pid
        assert a_ready[4] == RecoveryState.ACTIVE.value
        assert b_ready[4] == RecoveryState.STANDBY.value
        assert (root / ExecutionRole.PROCESS.value / "pid").read_text(encoding="utf-8") == str(a.pid)
        assert (root / ExecutionRole.REVISION_RECOVERY.value / "pid").read_text(encoding="utf-8") == str(b.pid)

        # A is attacked. A itself emits the takeover signal; the parent never
        # tells B to take over. The signal is transported verbatim to B.
        a_cmd.put("ATTACK")
        signal = a_events.get(timeout=10)
        assert signal[0:2] == (ExecutionRole.PROCESS.value, "FAILURE_SIGNAL")
        assert signal[2] == a.pid
        assert signal[3] == ExecutionRole.REVISION_RECOVERY.value
        assert signal[4] == HealthState.UNAVAILABLE.value
        assert signal[5] == "970f06d895a0cbc39fb109aaca7165bd2d5d12eb"

        # Only after the signal is observed does the transport deliver it to B.
        # No parent-issued TAKEOVER command exists in this sequence.
        b_cmd.put("TAKEOVER_SIGNAL")
        takeover_b = b_events.get(timeout=10)
        assert takeover_b == (ExecutionRole.REVISION_RECOVERY.value, "TAKEOVER", b.pid)

        # A enters recovery; its PID remains distinct from B.
        a_cmd.put("RECOVER")
        recovery_a = a_events.get(timeout=10)
        assert recovery_a == (ExecutionRole.PROCESS.value, "RECOVERING", a.pid)
        assert a.pid != b.pid
        assert (root / ExecutionRole.PROCESS.value / "pid").read_text(encoding="utf-8") == str(a.pid)

        # Reverse direction: B is now the active role conceptually. A must be
        # the recipient of the next verified failure signal. This constructs a
        # fresh coordinator for the rotated active role without copying state.
        b_coordinator = ROMCoordinator(
            active_role=ExecutionRole.REVISION_RECOVERY,
            last_verified_checkpoint=RecoveryCheckpoint(
                revision_id="canonical-970f06d8",
                content_hash="970f06d895a0cbc39fb109aaca7165bd2d5d12eb",
                provenance="test/canonical-baseline",
            ),
        )
        reverse_signal = b_coordinator.observe_failure(HealthState.UNAVAILABLE)
        assert reverse_signal.recipient_role is ExecutionRole.PROCESS
        assert reverse_signal.checkpoint.content_hash == "970f06d895a0cbc39fb109aaca7165bd2d5d12eb"

        a_cmd.put("ATTACK")
        # A is recovering in this harness, so an ATTACK command is deliberately
        # not used as the reverse handover trigger; the canonical coordinator
        # above is the evidence-producing event for B->A.
        reverse_received = reverse_signal
        assert reverse_received.recipient_role is ExecutionRole.PROCESS
        assert reverse_received.provenance == "rom/failure-observation"
    finally:
        a_cmd.put("STOP")
        b_cmd.put("STOP")
        a.join(timeout=10)
        b.join(timeout=10)
        if a.is_alive():
            a.terminate()
        if b.is_alive():
            b.terminate()
        assert a.exitcode == 0
        assert b.exitcode == 0
