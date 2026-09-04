import pytest

from lat_ces.umbrella import UmbrellaResult, red


def test_umbrella_red_preserves_reason_and_evidence():
    result = red(
        "F7 filter cannot be assigned to a wall.",
        element_id="wall-01",
        evidence="product category=filter",
        recommendation="Select a wall product.",
    )
    assert result.status == "RED"
    assert result.element_id == "wall-01"
    assert result.evidence == "product category=filter"
    assert result.recommendation == "Select a wall product."


def test_umbrella_rejects_unknown_status():
    with pytest.raises(ValueError):
        UmbrellaResult("BLUE", "invalid status")


def test_umbrella_rejects_empty_message():
    with pytest.raises(ValueError):
        UmbrellaResult("RED", "   ")
