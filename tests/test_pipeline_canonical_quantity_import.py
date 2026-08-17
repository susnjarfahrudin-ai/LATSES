"""Regression tests for legacy pipeline adapters after SCI quantity consolidation."""


def test_legacy_pipelines_import_canonical_quantity_layer():
    from lat_ces.modules.pipeline import FullPlenumSimulation
    from lat_ces.modules.pipeline_v3 import DuctNetworkSimulation
    from lat_ces.scientific.quantity import PhysicalQuantity

    assert FullPlenumSimulation is not None
    assert DuctNetworkSimulation is not None
    assert PhysicalQuantity is not None
