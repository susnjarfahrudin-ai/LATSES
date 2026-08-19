"""
LAT-CES Core: Scientific Knowledge Object (SKO)
Dokumenti: LAT-SCI-CORE-0004 do LAT-SCI-CORE-0008
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class SKOState(Enum):
    DRAFT = "DRAFT"
    RELEASED = "RELEASED"


@dataclass(init=False)
class ScientificKnowledgeObject:
    """
    Base class for all scientific entities in LAT-CES.
    Provides metadata, architectural constraints, traceability, and a
    one-way DRAFT -> RELEASED immutability boundary.
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
        if any(key in kwargs for key in ("sko_id", "title", "payload")):
            self._init_from_legacy(
                sko_id=kwargs.pop("sko_id", "SKO-UNSPECIFIED"),
                title=kwargs.pop("title", "Untitled SKO"),
                payload=kwargs.pop("payload", {}),
            )
            return

        # Rev A mode.
        self.name = kwargs.pop("name")
        self.object_type = kwargs.pop("object_type")
        self.definition = kwargs.pop("definition")
        self.assumptions = kwargs.pop("assumptions", [])
        self.limitations = kwargs.pop("limitations", [])
        self.created_by = kwargs.pop("created_by", "LAT-CES-Core")
        self.uuid = kwargs.pop("uuid", str(uuid4()))
        self.created_at = kwargs.pop("created_at", datetime.now(timezone.utc).isoformat())
        self.status = kwargs.pop("status", "Draft")
        self.approved_by = kwargs.pop("approved_by", None)

        self.sko_id = kwargs.pop("sko_id", f"SKO-{self.uuid[:8].upper()}")
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
        self.assumptions = self.payload.get("assumptions", [])
        self.limitations = self.payload.get("limitations", [])
        self.created_by = self.payload.get("created_by", "LAT-CES-Core")

        self.state = SKOState.DRAFT
        self._hash = None
        self._locked = False

    def approve(self, approved_by: str) -> None:
        """Promotes the SKO status to Approved with verification signature."""
        if self._locked:
            raise AttributeError("Released ScientificKnowledgeObject is immutable")
        if not approved_by:
            raise ValueError("approved_by must be a non-empty string")
        self.status = "Approved"
        self.approved_by = approved_by

    def deprecate(self, reason: str) -> None:
        """Marks the SKO as deprecated with an explicit rationale."""
        if self._locked:
            raise AttributeError("Released ScientificKnowledgeObject is immutable")
        self.status = "Deprecated"
        self.limitations.append(f"DEPRECATED: {reason}")

    def compute_hash(self) -> str:
        """Kriptografski SHA-256 hash nad kanonskim sadržajem objekta."""
        data = {
            "sko_id": self.sko_id,
            "title": self.title,
            "payload": self.payload,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def lock_and_release(self) -> str:
        """Hash the current canonical content and permanently release the SKO."""
        if self.state is SKOState.RELEASED or self._locked:
            raise ValueError("ScientificKnowledgeObject is already released")
        release_hash = self.compute_hash()
        object.__setattr__(self, "_hash", release_hash)
        object.__setattr__(self, "status", "Released")
        object.__setattr__(self, "state", SKOState.RELEASED)
        object.__setattr__(self, "_locked", True)
        return release_hash

    def __repr__(self) -> str:
        return f"SKO({self.sko_id}: {self.title})"
