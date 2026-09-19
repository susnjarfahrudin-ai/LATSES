from lat_ces.adapters.scene1_native import Scene1NativePresentation


def test_scene1_consumes_scene_v1_and_emits_only_2d_primitives():
    scene = {
        "schema": "scene.v1",
        "projection": {
            "walls": [{"start": [0, 0], "end": [4, 0]}],
            "openings": [{"type": "window", "position": [2, 0]}],
            "rooms": [{"name": "living", "boundary": [[0, 0], [4, 0], [4, 3], [0, 3]]}],
            "ignored_3d": [{"mesh": "external"}],
        },
    }

    result = Scene1NativePresentation().present(scene)

    assert result["scene"] == "scene1"
    assert set(result["primitives"]) == {"walls", "openings", "rooms"}
    assert result["primitives"]["walls"] == scene["projection"]["walls"]


def test_scene1_has_no_model_write_surface():
    assert not hasattr(Scene1NativePresentation, "update_model")
    assert not hasattr(Scene1NativePresentation, "set_model")
    assert not hasattr(Scene1NativePresentation, "write_model")
