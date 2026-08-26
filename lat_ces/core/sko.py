"""
LAT-CES Core: Scientific Knowledge Object (SKO)
Documents: LAT-SCI-CORE-0004 through LAT-SCI-CORE-0008.

This module is the canonical ScientificKnowledgeObject lifecycle boundary.
Domain modules must not create a parallel scientific-knowledge identity system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SKOState(Enum):
    DRAFT = "DRAFT"
    RELEASED = "RELEASED"


def _semantic_type_token(object_type: str) -> str:
    """Return a portable identifier token for an SKO object type."""
    token = re.sub(r"[^A-Za-z0-9]+", "-", str(object_type).upper()).strip("-")
    return token or "GENERIC"


@dataclass(init=False)
class ScientificKnowledgeObject:
    """
    Canonical knowledge identity and lifecycle boundary for LAT-CES scientific
    and engineering knowledge objects.

    The positional/legacy constructor remains supported for compatibility.
    New code should prefer the named constructor so semantic identity,
    provenance and predecessor/version metadata are explicit.
    """

    name: str
    object_type: str
    definition: str
    assumptions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    created_by: str = "LAT-CES-Core"
    uuid: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "Draft"
    approved_by: Optional[str] = None

    # Universal identity and lifecycle metadata.
    semantic_id: str = ""
    version: str = "1.0"
    predecessor_id: Optional[str] = None
    provenance: Dict[str, Any] = field(default_factory=dict)
    verification_refs: List[str] = field(default_factory=list)
    validation_refs: List[str] = field(default_factory=list)
    released_at: Optional[str] = None
    release_hash: Optional[str] = None

    # Backward-compatible attributes used by existing code.
    sko_id: str = ""
    title: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    state: SKOState = SKOState.DRAFT
    _hash: Optional[str] = None
    _locked: bool = False

    def __setattr__(self, name: str, value: Any) -> None:
        """Reject public mutation after the SKO has been released."""
        if getattr(self, "_locked", False) and not name.startswith("_"):
            raise AttributeError("Released ScientificKnowledgeObject is immutable")
        object.__setattr__(self, name, value)

    def __init__(self, *args, **kwargs):
        # Legacy positional mode: ScientificKnowledgeObject(sko_id, title, payload)
        if len(args) == 3 and isinstance(args[2], dict):
            sko_id, title, payload = args
            self._init_from_legacy(sko_id=sko_id, title=title, payload=payload)
            return

        # Legacy keyword mode commonly used by upstream modules.
        if any(key in kwargs for key in ("sko_id", "title", "payload")) and "name" not in kwargs:
            self._init_from_legacy(
                sko_id=kwargs.pop("sko_id", "SKO-UNSPECIFIED"),
                title=kwargs.pop("title", "Untitled SKO"),
                payload=kwargs.pop("payload", {}),
            )
            return

        self.name = kwargs.pop("name")
        self.object_type = kwargs.pop("object_type")
        self.definition = kwargs.pop("definition")
        self.assumptions = list(kwargs.pop("assumptions", []))
        self.limitations = list(kwargs.pop("limitations", []))
        self.created_by = kwargs.pop("created_by", "LAT-CES-Core")
        self.uuid = kwargs.pop("uuid", str(uuid4()))
        self.created_at = kwargs.pop("created_at", datetime.now(timezone.utc).isoformat())
        self.status = kwargs.pop("status", "Draft")
        self.approved_by = kwargs.pop("approved_by", None)

        self.sko_id = kwargs.pop("sko_id", f"SKO-{self.uuid[:8].upper()}")
        self.semantic_id = kwargs.pop(
            "semantic_id",
            f"LAT-SKO-{_semantic_type_token(self.object_type)}-{self.uuid[:8].upper()}",
        )
        self.version = str(kwargs.pop("version", "1.0"))
        self.predecessor_id = kwargs.pop("predecessor_id", None)
        self.provenance = dict(kwargs.pop("provenance", {}))
        self.verification_refs = list(kwargs.pop("verification_refs", []))
        self.validation_refs = list(kwargs.pop("validation_refs", []))
        self.released_at = kwargs.pop("released_at", None)
        self.release_hash = kwargs.pop("release_hash", None)

        self.title = kwargs.pop("title", self.name)
        self.payload = kwargs.pop(
            "payload",
            {
                "object_type": self.object_type,
                "definition": self.definition,
                "assumptions": self.assumptions,
                "limitations": self.limitations,
                "created_by": self.created_by,
            },
        )

        self.state = SKOState.DRAFT
        self._hash = None
        self._locked = False

    def _init_from_legacy(self, sko_id: str, title: str, payload: Dict[str, Any]) -> None:
        self.uuid = str(uuid4())
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.status = "Draft"
        self.approved_by = None

        self.sko_id = sko_id
        self.title = title
        self.payload = payload or {}

        self.name = title
        self.object_type = self.payload.get("object_type", "Generic")
        self.definition = self.payload.get("definition", "")
        self.assumptions = list(self.payload.get("assumptions", []))
        self.limitations = list(self.payload.get("limitations", []))
        self.created_by = self.payload.get("created_by", "LAT-CES-Core")

        self.semantic_id = f"LAT-SKO-{_semantic_type_token(self.object_type)}-{self.uuid[:8].upper()}"
        self.version = "1.0"
        self.predecessor_id = None
        self.provenance = {}
        self.verification_refs = []
        self.validation_refs = []
        self.released_at = None
        self.release_hash = None

        self.state = SKOState.DRAFT
        self._hash = None
        self._locked = False

    def approve(self, approved_by: str) -> None:
        """Promote the SKO to Approved before final release."""
        if self._locked:
            raise AttributeError("Released ScientificKnowledgeObject is immutable")
        if not approved_by:
            raise ValueError("approved_by must be a non-empty string")
        self.status = "Approved"
        self.approved_by = approved_by

    def deprecate(self, reason: str) -> None:
        """Mark the SKO as deprecated with an explicit rationale."""
        if self._locked:
            raise AttributeError("Released ScientificKnowledgeObject is immutable")
        if not reason:
            raise ValueError("reason must be a non-empty string")
        self.status = "Deprecated"
        self.limitations.append(f"DEPRECATED: {reason}")

    def compute_hash(self) -> str:
        """Compute SHA-256 over the canonical scientific identity/content record."""
        data = {
            "semantic_id": self.semantic_id,
            "sko_id": self.sko_id,
            "version": self.version,
            "predecessor_id": self.predecessor_id,
            "object_type": self.object_type,
            "name": self.name,
            "title": self.title,
            "definition": self.definition,
            "assumptions": self.assumptions,
            "limitations": self.limitations,
            "provenance": self.provenance,
            "verification_refs": self.verification_refs,
            "validation_refs": self.validation_refs,
            "payload": self.payload,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def lock_and_release(self) -> str:
        """Hash the current record and permanently release the SKO."""
        if self.state is SKOState.RELEASED or self._locked:
            raise ValueError("ScientificKnowledgeObject is already released")
        release_hash = self.compute_hash()
        object.__setattr__(self, "_hash", release_hash)
        object.__setattr__(self, "release_hash", release_hash)
        object.__setattr__(self, "released_at", datetime.now(timezone.utc).isoformat())
        object.__setattr__(self, "status", "Released")
        object.__setattr__(self, "state", SKOState.RELEASED)
        object.__setattr__(self, "_locked", True)
        return release_hash

    def __repr__(self) -> str:
        return f"SKO({self.semantic_id}: {self.title})"
