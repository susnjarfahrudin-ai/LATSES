from lat_ces.building.model import BuildingModel, Level, Roof
from lat_ces.building_engineering_ui import BuildingEngineeringShell


def test_engineering_shell_commands_are_canonical():
    labels = [label for label, _command in BuildingEngineeringShell.COMMANDS]
    assert labels == [
        "Model",
        "Katalog",
        "Tlocrt",
        "Presjek",
        "3D",
        "Konstrukcija",
        "MEP",
        "Provjera",
        "Izvještaj",
    ]


def test_building_model_is_the_only_shell_source_of_truth():
    model = BuildingModel("Referentna kuća")
    model.add_level(Level("Prizemlje", elevation=0.0, height=2.8))
    model.set_roof(Roof(roof_type="dvovodni", length_m=12.0, width_m=10.0, slope_deg=35.0))

    assert model.floor_area == 0.0
    assert model.volume == 0.0
    assert len(model.levels) == 1
    assert model.roof is not None
    assert model.roof.roof_type == "dvovodni"
