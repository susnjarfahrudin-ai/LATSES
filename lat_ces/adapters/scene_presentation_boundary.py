"""One-way presentation boundary for canonical ``scene.v1`` snapshots.

The canonical BuildingModel/scene snapshot is upstream truth.  This module only
projects that snapshot toward presentation consumers; no presentation result
is accepted back into LAT-CES engineering state.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .visualization_2d import adapt_scene_2d
from .visualization_3d import adapt_scene_3d


class Scene1PresentationBoundary:
    """One-way boundary from ``scene.v1`` to the native 2D presentation payload."""

    def present(self, scene: Mapping[str, Any]) -> Dict[str, Any]:
        """Return the renderer-neutral Scene 1 payload.

        The returned object is a derived presentation value.  It is never used
        as an engineering-model input by this boundary.
        """
        return adapt_scene_2d(dict(scene))


class Scene2PresentationBoundary:
    """One-way boundary from ``scene.v1`` to an external 3D process."""

    def export(self, scene: Mapping[str, Any], path: Path) -> Path:
        """Write the 3D presentation payload for an external renderer."""
        payload = adapt_scene_3d(dict(scene))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return path

    def launch(
        self,
        scene: Mapping[str, Any],
        path: Path,
        executable: Sequence[str],
    ) -> subprocess.Popen[bytes]:
        """Launch an external renderer using only the exported presentation file.

        No stdout/stderr/result from the external process is interpreted as
        engineering data.  The communication direction is LAT-CES -> file ->
        external process only.
        """
        self.export(scene, path)
        return subprocess.Popen([*executable, str(path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
