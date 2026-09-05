from lat_ces.architecture_visualization import EngineeringArchitectureView


def test_architecture_view_is_available_for_workspace_navigation():
    assert EngineeringArchitectureView is not None
    assert hasattr(EngineeringArchitectureView, "__init__")
