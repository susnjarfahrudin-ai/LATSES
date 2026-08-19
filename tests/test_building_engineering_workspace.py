from lat_ces.building_engineering_workspace import ENGINEERING_MODULES


def test_workspace_has_single_engineering_module_registry():
    keys = [module.key for module in ENGINEERING_MODULES]
    assert len(keys) == len(set(keys))
    assert {"model", "draft", "air", "heat", "cool", "water", "drain", "electric", "solar", "structure"} <= set(keys)


def test_workspace_contains_analysis_and_human_decision_layers():
    modules = {module.key: module for module in ENGINEERING_MODULES}
    assert {"light", "materials", "quantities", "energy", "acoustics", "service", "ai"} <= modules.keys()
    assert "čovjek" in modules["ai"].description.lower()


def test_airflow_module_is_central_space_flow_module():
    air = next(module for module in ENGINEERING_MODULES if module.key == "air")
    assert "Airflow Through Space" in air.description
    assert "uzgon" in air.description.lower()
