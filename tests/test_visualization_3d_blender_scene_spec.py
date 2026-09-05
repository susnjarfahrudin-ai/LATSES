from dataclasses import FrozenInstanceError

import pytest

from lat_ces.visualization_3d_adapter import BuildingScene3D, SceneBox3D, SceneObject3D
from lat_ces.visualization_3d_backend_handoff import to_visualization_3d_backend_envelope
from lat_ces.visualization_3d_blender_scene_spec import (
    BlenderSceneSpec,
    to_blender_scene_specs,
)


def make_envelope():
    scene = BuildingScene3D(
        building_model_id="BM-3D-001",
        source_ref="building-model:BM-3D-001",
        objects=(
            SceneObject3D(
                visual_object_id="wall:001",
                source_element_id="WALL-001",
                element_type="wall",
                geometry=SceneBox3D(0.0, 0.0, 2.0, 6.0, 0.2, 3.0, 0.0),
                role="solid",
                material_ref="MAT-001",
                name="North wall",
            ),
            SceneObject3D(
                visual_object_id="opening:001",
                source_element_id="OPN-001",
                element_type="opening",
                geometry=SceneBox3D(1.5, 0.0, 2.0, 1.2, 0.2, 1.4, 0.0),
                role="void",
                material_ref=None,
                name="window",
            ),
        ),
    )
    return to_visualization_3d_backend_envelope(scene, "blender")


def test_blender_scene_specs_preserve_identity_and_geometry():
    envelope = make_envelope()

    specs = to_blender_scene_specs(envelope)

    assert specs[0] == BlenderSceneSpec(
        building_model_id="BM-3D-001",
        source_ref="building-model:BM-3D-001",
        object_id="wall:001",
        source_element_id="WALL-001",
        primitive="box",
        location=(0.0, 0.0, 2.0),
        dimensions=(6.0, 0.2, 3.0),
        rotation_z_deg=0.0,
        role="solid",
        material_ref="MAT-001",
    )
    assert specs[1].role == "void"
    assert specs[1].dimensions == (1.2, 0.2, 1.4)


def test_blender_scene_specs_are_immutable():
    spec = to_blender_scene_specs(make_envelope())[0]

    with pytest.raises(FrozenInstanceError):
        spec.object_id = "changed"


def test_blender_scene_specs_require_blender_target():
    scene = make_envelope().scene
    paraview_envelope = to_visualization_3d_backend_envelope(scene, "paraview")

    with pytest.raises(ValueError, match="Blender scene specs require a blender backend envelope"):
        to_blender_scene_specs(paraview_envelope)
