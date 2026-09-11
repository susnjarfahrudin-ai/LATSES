from pathlib import Path

from lat_ces.presentation_controller import PresentationController


class Scene1Spy:
    def __init__(self):
        self.received = None

    def present(self, scene):
        self.received = scene
        return {"consumer": "scene1"}


class Scene2Spy:
    def __init__(self):
        self.exported = None
        self.launched = None

    def export(self, scene, path):
        self.exported = (scene, path)
        return path

    def launch(self, scene, path, executable):
        self.launched = (scene, path, executable)
        return "external-process"


def test_controller_routes_same_snapshot_without_owning_it(tmp_path: Path):
    scene = {
        "schema": "latces.visualization.scene.v1",
        "source": "BuildingModel",
        "building": {"name": "Reference"},
    }
    scene1 = Scene1Spy()
    scene2 = Scene2Spy()
    controller = PresentationController(scene1=scene1, scene2=scene2)
    export_path = tmp_path / "scene.json"

    assert controller.present_scene_1(scene) == {"consumer": "scene1"}
    assert controller.export_scene_2(scene, export_path) == export_path
    assert controller.launch_scene_2(scene, export_path, ["blender", "--background"]) == "external-process"

    assert scene1.received is scene
    assert scene2.exported == (scene, export_path)
    assert scene2.launched == (scene, export_path, ["blender", "--background"])
    assert scene["source"] == "BuildingModel"


def test_controller_has_no_model_write_or_reverse_presentation_api():
    public_names = {
        name for name in dir(PresentationController) if not name.startswith("_")
    }

    assert public_names == {
        "export_scene_2",
        "launch_scene_2",
        "present_scene_1",
    }
