from dataclasses import FrozenInstanceError

import pytest

from lat_ces.visualization_3d_adapter import (
    BuildingScene3D,
    SceneBox3D,
    SceneObject3D,
)
from lat_ces.visualization_3d_backend_handoff import (
    Visualization3DBackendEnvelope,
    to_visualization_3d_backend_envelope,
)


def _scene() -> BuildingScene3D:
    return BuildingScene3D(
        building_model_id="building-001",
        source_ref="building-model:building-001",
        objects=(
            SceneObject3D(
                visual_object_id="wall:001",
                source_element_id="wall-001",
                element_type="wall",
                geometry=SceneBox3D(
                    origin_x_m=0.0,
                    origin_y_m=0.0,
                    origin_z_m=0.0,
                    length_m=5.0,
                    width_m=0.2,
                    height_m=3.0,
                ),
            ),
        ),
    )


def test_handoff_preserves_canonical_identity_and_scene() -> None:
    scene = _scene()

    envelope = to_visualization_3d_backend_envelope(scene, "blender")

    assert isinstance(envelope, Visualization3DBackendEnvelope)
    assert envelope.backend == "blender"
    assert envelope.contract_version == "LAT-VIS-3D-HANDOFF-1"
    assert envelope.building_model_id == scene.building_model_id
    assert envelope.source_ref == scene.source_ref
    assert envelope.scene is scene
    assert envelope.status == scene.status


def test_handoff_supports_paraview_without_changing_scene() -> None:
    scene = _scene()

    envelope = to_visualization_3d_backend_envelope(
        scene, "paraview", contract_version="LAT-VIS-3D-HANDOFF-1"
    )

    assert envelope.backend == "paraview"
    assert envelope.scene is scene


def test_handoff_is_immutable() -> None:
    envelope = to_visualization_3d_backend_envelope(_scene(), "blender")

    with pytest.raises(FrozenInstanceError):
        envelope.backend = "paraview"


def test_handoff_rejects_unsupported_backend() -> None:
    with pytest.raises(ValueError, match="unsupported 3-D renderer backend"):
        to_visualization_3d_backend_envelope(_scene(), "openfoam")  # type: ignore[arg-type]


def test_handoff_rejects_empty_contract_version() -> None:
    with pytest.raises(ValueError, match="contract_version is required"):
        to_visualization_3d_backend_envelope(_scene(), "blender", contract_version=" ")
