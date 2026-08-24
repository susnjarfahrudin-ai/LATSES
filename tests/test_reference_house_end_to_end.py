import json
from pathlib import Path


def test_reference_house_end_to_end_fixture_contract():
    path = Path(__file__).parents[1] / "examples" / "reference_house" / "reference_house_4storey.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    storeys = data["storeys"]
    assert len(storeys) == 4
    assert storeys[0]["name"] == "Prizemlje"
    assert [s["name"] for s in storeys[1:]] == ["Sprat 1", "Sprat 2", "Sprat 3"]
    assert data["roof"]["type"] == "gable"
    assert data["acceptance"]["minimum_storeys"] == 4
    assert data["acceptance"]["requires_ground_floor"] is True
    assert data["acceptance"]["requires_three_upper_storeys"] is True
    assert data["acceptance"]["requires_statics_handoff"] is True
    assert data["acceptance"]["requires_mep_systems"] is True
    assert set(data["systems"]) >= {
        "water_supply", "drainage", "electrical", "heating",
        "cooling", "ventilation", "acoustics"
    }
    assert set(data["nodes"]) >= {
        "utility_room", "water_main", "electrical_main",
        "heat_source", "ventilation_unit"
    }
