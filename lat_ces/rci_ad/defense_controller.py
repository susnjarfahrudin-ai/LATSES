"""Central RCI-AD decision authority; enforcement remains separate."""
from __future__ import annotations
from dataclasses import dataclass
from .defense_decision import DefenseAction, DefenseDecision
from .status import DefenseStatus, IntegrityStatus, TrustStatus

@dataclass(frozen=True)
class DefenseInput:
    resource_pressure: float
    communication_pressure: float
    packet_weight: float
    resource_feasibility: float
    confidence: float
    integrity: IntegrityStatus
    trust: TrustStatus
    hard_constraint: bool=False
    source_id: str="rci-ad"
    sequence: int=0

class DefenseController:
    def decide(self, evidence: DefenseInput) -> DefenseDecision:
        if evidence.integrity in (IntegrityStatus.COMPROMISED, IntegrityStatus.MODIFIED) or evidence.trust is TrustStatus.REVOKED:
            action=DefenseAction.ISOLATE
        elif evidence.hard_constraint or evidence.resource_feasibility >= 1.0:
            action=DefenseAction.DROP
        elif max(evidence.resource_pressure,evidence.communication_pressure,evidence.packet_weight) >= .8:
            action=DefenseAction.THROTTLE
        elif max(evidence.resource_pressure,evidence.communication_pressure) >= .5:
            action=DefenseAction.OBSERVE
        else:
            action=DefenseAction.ALLOW
        return DefenseDecision(action=action,reason="canonical RCI-AD policy evaluation",source_id=evidence.source_id,sequence=evidence.sequence)
