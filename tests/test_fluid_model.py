from math import pi
import pytest
from lat_ces.building.fluid import FluidNetwork, FluidNode, FluidSegment, pressure_loss_pa

def test_segment_area_is_deterministic() -> None:
    segment = FluidSegment("s1", "n1", "n2", 10.0, 0.1)
    assert segment.area_m2 == pytest.approx(pi * 0.1**2 / 4.0)

def test_laminar_pressure_loss_is_positive() -> None:
    segment = FluidSegment("s1", "n1", "n2", 10.0, 0.1)
    loss = pressure_loss_pa(segment, 0.001, 1000.0, 0.001)
    assert loss > 0.0

def test_network_rejects_unknown_nodes() -> None:
    network = FluidNetwork(nodes=(FluidNode("n1"),), segments=(FluidSegment("s1", "n1", "n2", 1.0, 0.1),))
    with pytest.raises(ValueError, match="unknown node"):
        network.validate()
