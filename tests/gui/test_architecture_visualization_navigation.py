from lat_ces.architecture_visualization import ArchitectureVisualizationView


def test_architecture_view_is_available_for_workspace_navigation():
    assert ArchitectureVisualizationView is not None
    assert hasattr(ArchitectureVisualizationView, "__init__")
