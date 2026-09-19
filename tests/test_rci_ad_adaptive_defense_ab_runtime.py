"""Integrated adversarial runtime acceptance for the post-#286 security chain.

The harness intentionally keeps the production components unchanged. Two
isolated OS processes execute the same canonical chain:

CyberFortress -> Secure IPC -> FlowGuard -> RCI-AD -> AdaptiveDefense
-> verified DefenseRecord -> A/B handover -> recovery -> next observation.

The parent injects only authenticated test traffic and attack stimuli; it never
issues TAKEOVER or RECOVER commands. Only verified evidence crosses the A/B
boundary, and peer runtime/model state is never transferred.
"""

from __future__ import annotations

import multiprocessing as mp
import os
from pathlib import Path
import time

import pytest

from lat_ces.rci_ad.defense_contract import bind_flow_observation_to_defense
from lat_ces.rci_ad.flow_observation import observe_flow
from lat_ces.security.adaptive_defense import AdaptiveDefense, DefenseRecord
from lat_ces.security.cyber_fortress import CyberFortress
from lat_ces.security.flow_guard import FlowGuard
from lat_ces.security.secure_ipc import SignedIPCChannel
from lat_ces.structural.role_handover import (
    ExecutionRole,
    HealthState,
    RecoveryCheckpoint,
    RecoveryState,
    RecoveryStateMachine,
    ROMCoordinator,
)

_TIMEOUT = 15.0
_SECRET = b"latces-integrated-runtime-test-secret"
_ATTACKER_IP = "198.51.100.10"  # RFC 5737 TEST-NET-2; valid for threat-score IP parsing.
_BASELINE = {name: 100.0 for name in ("frequency", "volume", "concurrency", "novelty")}


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

    ipc = SignedIPCChannel(_SECRET)
    fortress = CyberFortress(ipc)
    guard = FlowGuard(_BASELINE)
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

    event_out.send({"event": "READY", "role": role.value, "pid": pid, "state": machine.state.value})

    while True:
        if peer_in.poll(0.05):
            message = peer_in.recv()
        elif control_in.poll(0.05):
            message = control_in.recv()
        else:
            continue
        command = message["command"]

        if command == "ATTACK":
            if machine.active_role is not role:
                event_out.send({"event": "REJECTED_ATTACK", "role": role.value, "pid": pid})
                continue

            packet = message["packet"]
            payload = fortress.receive(_ATTACKER_IP, packet)
            observed = payload["flow"]

            observations = []
            observation = observe_flow(
                guard,
                observed,
                observations.append,
                timestamp=message["timestamp"],
            )
            assert observations == [observation]
            assert observation.decision.allowed is False

            record = bind_flow_observation_to_defense(
                defense,
                observation,
                invariant_id=message["invariant_id"],
                attack_class=message["attack_class"],
                source=role.value,
            )
            defense.quarantine(record)
            verified = defense.promote(
                record,
                verification_sha=message["verification_sha"],
            )
            assert verified.verified is True

            health = HealthState[message["health"]]
            machine = machine.on_failure(health)
            signal = ROMCoordinator(role, baseline).observe_failure(health)

            (root / "attack.json").write_text(
                "attack=" + message["attack_id"] + "\n"
                + "pid=" + str(pid) + "\n"
                + "record=" + verified.digest + "\n",
                encoding="utf-8",
            )

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
                    "limiting_dimension": observation.limiting_dimension,
                    "max_deviation": observation.decision.max_deviation,
                    "verified": verified.verified,
                    "record_digest": verified.digest,
                }
            )
            continue

        if command == "HANDOVER":
            if message["recipient_role"] != role.value:
                raise AssertionError("handover delivered to wrong role")
            record = message["record"]
            if not isinstance(record, DefenseRecord):
                raise AssertionError("handover must carry a DefenseRecord")
            if not record.verified or not record.verification_sha:
                raise AssertionError("unverified defense crossed A/B boundary")
            defense.import_verified(record)
            if machine.state not in {RecoveryState.STANDBY, RecoveryState.READY}:
                raise AssertionError(f"automatic takeover requires STANDBY or READY, got {machine.state}")
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
                "checkpoint=" + checkpoint.revision_id + "\n" + "pid=" + str(pid) + "\n",
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
                    "flow_baseline": guard.baseline,
                }
            )
            continue

        if command == "STOP":
            event_out.send({"event": "STOPPED", "role": role.value, "pid": pid})
            return

        raise AssertionError(f"unknown command: {command}")


def _attack_packet(attack_id: str, frequency: float) -> bytes:
    return SignedIPCChannel(_SECRET).pack(
        {"attack_id": attack_id, "flow": {**_BASELINE, "frequency": frequency}},
        sender_id=_ATTACKER_IP,
    )


def test_integrated_adversarial_rci_ad_adaptive_defense_ab_rotation(tmp_path: Path) -> None:
    """Exercise the complete integrated chain in both A -> B and B -> A directions."""
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
        name="LATCES-A",
    )
    b = ctx.Process(
        target=_runtime,
        args=(ExecutionRole.REVISION_RECOVERY, b_control_in, b_event_out, a_to_b_recv, b_to_a_send, str(b_dir)),
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

        a_control_send.send(
            {
                "command": "ATTACK",
                "attack_id": "integrated-A-001",
                "packet": _attack_packet("integrated-A-001", 125.0),
                "timestamp": 123.0,
                "invariant_id": "flow:frequency:1250",
                "attack_class": "flowguard/4d-pressure",
                "health": "DEGRADED",
                "verification_sha": "sha256:verified-A-001",
            }
        )
        failure_a = _recv(a_event_recv)
        takeover_b = _recv(b_event_recv)
        recovered_a = _recv(a_event_recv)

        assert failure_a["event"] == "FAILURE"
        assert failure_a["pid"] == a.pid
        assert failure_a["limiting_dimension"] == "frequency"
        assert failure_a["max_deviation"] == 0.25
        assert failure_a["verified"] is True
        assert takeover_b["event"] == "TAKEOVER"
        assert takeover_b["pid"] == b.pid
        assert takeover_b["active_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_b["source_role"] == ExecutionRole.PROCESS.value
        assert takeover_b["record_imported"] is True
        assert takeover_b["peer_runtime_transferred"] is False
        assert recovered_a["event"] == "RECOVERED"
        assert recovered_a["pid"] == a.pid
        assert recovered_a["state"] == RecoveryState.READY.value

        b_control_send.send(
            {
                "command": "ATTACK",
                "attack_id": "integrated-B-001",
                "packet": _attack_packet("integrated-B-001", 130.0),
                "timestamp": 124.0,
                "invariant_id": "flow:frequency:1300",
                "attack_class": "flowguard/4d-pressure",
                "health": "UNAVAILABLE",
                "verification_sha": "sha256:verified-B-001",
            }
        )
        failure_b = _recv(b_event_recv)
        takeover_a = _recv(a_event_recv)
        recovered_b = _recv(b_event_recv)

        assert failure_b["event"] == "FAILURE"
        assert failure_b["pid"] == b.pid
        assert failure_b["limiting_dimension"] == "frequency"
        assert failure_b["max_deviation"] == pytest.approx(0.30)
        assert failure_b["verified"] is True
        assert takeover_a["event"] == "TAKEOVER"
        assert takeover_a["pid"] == a.pid
        assert takeover_a["active_role"] == ExecutionRole.PROCESS.value
        assert takeover_a["source_role"] == ExecutionRole.REVISION_RECOVERY.value
        assert takeover_a["record_imported"] is True
        assert takeover_a["peer_runtime_transferred"] is False
        assert recovered_b["event"] == "RECOVERED"
        assert recovered_b["pid"] == b.pid
        assert recovered_b["state"] == RecoveryState.READY.value

        assert a.is_alive() and b.is_alive()

        a_control_send.send({"command": "SNAPSHOT"})
        final_a = _recv(a_event_recv)
        b_control_send.send({"command": "SNAPSHOT"})
        final_b = _recv(b_event_recv)
        assert final_a["pid"] == a.pid and final_b["pid"] == b.pid
        assert final_a["active_role"] == ExecutionRole.PROCESS.value
        assert final_b["active_role"] == ExecutionRole.PROCESS.value
        assert final_a["flow_baseline"] == _BASELINE
        assert final_b["flow_baseline"] == _BASELINE
        assert "attack.json" in final_a["state_files"] and "recovery.json" in final_a["state_files"]
        assert "attack.json" in final_b["state_files"] and "recovery.json" in final_b["state_files"]
        assert len(final_a["defense_records"]) == 2
        assert len(final_b["defense_records"]) == 2
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
