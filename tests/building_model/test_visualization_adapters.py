from lat_ces.adapters.visualization_2d import adapt_scene_2d
from lat_ces.adapters.visualization_3d import adapt_scene_3d


SCENE = {
    "schema": "latces.visualization.scene.v1",
    "source": "BuildingModel",
    "building": {"name": "Reference House"},
    "levels": [
        {
            "id": "L1",
            "name": "Ground Floor",
            "length_m": 10.0,
            "width_m": 8.0,
            "height_m": 2.8,
            "rooms": [{"id": "R1", "name": "Living"}],
            "walls": [
                {
                    "id": "W1",
                    "length_m": 10.0,
                    "thickness_m": 0.25,
                    "height_m": 2.8,
                    "exterior": True,
                    "load_bearing": True,
                    "placement": {"x1_m": 0.0, "y1_m": 0.0, "x2_m": 10.0, "y2_m": 0.0},
                    "openings": [
                        {
                            "kind": "window",
                            "width_m": 1.2,
                            "height_m": 1.4,
                            "sill_height_m": 0.9,
                            "position_m": 2.0,
                        }
                    ],
                }
            ],
        }
    ],
}


def test_2d_adapter_preserves_authoritative_wall_geometry():
    projected = adapt_scene_2d(SCENE)
    wall = projected["levels"][0]["walls"][0]

    assert projected["schema"] == "latces.visualization.2d.v1"
    assert projected["source_schema"] == SCENE["schema"]
    assert wall["id"] == "W1"
    assert (wall["x1_m"], wall["y1_m"]) == (0.0, 0.0)
    assert (wall["x2_m"], wall["y2_m"]) == (10.0, 0.0)
    assert wall["thickness_m"] == 0.25
    assert wall["openings"] == SCENE["levels"][0]["walls"][0]["openings"]


def test_3d_adapter_preserves_authoritative_wall_geometry():
    projected = adapt_scene_3d(SCENE)
    wall = projected["levels"][0]["walls"][0]

    assert projected["schema"] == "latces.visualization.3d.v1"
    assert projected["source_schema"] == SCENE["schema"]
    assert wall["id"] == "W1"
    assert wall["start_m"] == [0.0, 0.0, 0.0]
    assert wall["end_m"] == [10.0, 0.0, 0.0]
    assert wall["height_m"] == 2.8
    assert wall["thickness_m"] == 0.25


def test_adapters_reject_unknown_source_schema():
    invalid = dict(SCENE)
    invalid["schema"] = "unknown"

    try:
        adapt_scene_2d(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("2D adapter accepted an unknown schema")

    try:
        adapt_scene_3d(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("3D adapter accepted an unknown schema")
