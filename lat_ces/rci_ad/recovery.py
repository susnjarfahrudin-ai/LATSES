"""Trusted-artifact recovery planning; no process cloning or implicit trust."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RecoveryPlan:
    target_id:str
    trusted_artifact:str
    known_good_configuration:str
    actions:tuple[str,...]

def plan_recovery(target_id:str, trusted_artifact:str, known_good_configuration:str)->RecoveryPlan:
    if not target_id or not trusted_artifact or not known_good_configuration: raise ValueError("recovery identities are required")
    return RecoveryPlan(target_id,trusted_artifact,known_good_configuration,("DETECT","REVOKE","ISOLATE","VERIFY_CLEAN_ARTIFACT","FRESH_INSTANCE","SELF_TEST","REVALIDATE","REINTEGRATE"))
