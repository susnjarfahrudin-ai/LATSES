import json

from lat_ces.building.engineering_report import build_building_engineering_report
from lat_ces.building.floor_plan import Point2D, Segment2D, Wall
from lat_ces.building.model import BuildingModel, Level, Material, Roof
from lat_ces.building.project_io import load_workflow, save_workflow
from lat_ces.building.structural import calculate_structural_loads
from lat_ces.building.mep import ensure_mep_registry
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch
from lat_ces.building.workflow import BuildingWorkflow


def test_roof_dimensions_and_loads_are_real_model_data():
    model = BuildingModel(name="Roof test")
    model.set_roof(Roof("Četverovodni", length_m=12.0, width_m=9.0, slope_deg=25.0, height_m=2.4, dead_load_kpa=0.8, snow_load_kpa=1.2))
    assert model.roof.plan_area_m2 == 108.0
    assert model.roof.dead_load_kpa == 0.8
    assert model.roof.snow_load_kpa == 1.2


def test_load_bearing_wall_produces_preliminary_line_load():
    model = BuildingModel(name="Structure test")
    level = model.add_level(Level("Prizemlje", 0.0, 2.8, length_m=10.0, width_m=10.0, dead_load_kpa=0.8, live_load_kpa=2.0))
    level.set_floor_plan(__import__("lat_ces.building.floor_plan", fromlist=["FloorPlan"]).FloorPlan("Prizemlje"))
    material = model.add_material(Material("Beton", density=2500.0, youngs_modulus=30e9, thermal_conductivity=2.1))
    wall = Wall("Nosivi zid", Segment2D(Point2D(0, 0), Point2D(10, 0)), thickness=0.20, load_bearing=True, material_id=material.material_id, tributary_width_m=2.0)
    level.floor_plan.add_wall(wall)
    model.set_roof(Roof("Ravni", length_m=10.0, width_m=10.0, dead_load_kpa=0.5, snow_load_kpa=1.0))

    report = calculate_structural_loads(model)
    assert report.status == "CALCULATED"
    assert report.walls[0].total_line_load_kn_m > report.walls[0].self_weight_kn_m
    assert report.total_vertical_line_load_kn_m > 0.0


def test_mep_and_envelope_survive_save_load(tmp_path):
    model = BuildingModel(name="Persistence test")
    level = model.add_level(Level("Prizemlje", 0.0, 2.8, length_m=10.0, width_m=10.0, facade_finish="Silikatna žbuka", insulation_material="MW", insulation_thickness_m=0.16, interior_plaster_material="Cementno-krečna žbuka", interior_plaster_thickness_m=0.015))
    from lat_ces.building.floor_plan import FloorPlan
    level.set_floor_plan(FloorPlan("Prizemlje"))
    registry = ensure_mep_registry(model)
    registry.add_ventilation_opening(VentilationOpening("VO-1", "R1", "supply", 0.1))
    registry.add_water_branch(WaterBranch("WB-1", "R1", "cold_water", 0.02, 0.0002, length_m=5.0))
    registry.add_heating_zone(HeatingZone("HZ-1", "R1", "underfloor", 35.0, 28.0, room_heat_load_w=10000.0))
    workflow = BuildingWorkflow(model=model)
    target = tmp_path / "building.json"
    save_workflow(workflow, target)
    reloaded = load_workflow(target)
    assert reloaded.model.levels[next(iter(reloaded.model.levels))].insulation_thickness_m == 0.16
    reloaded_registry = ensure_mep_registry(reloaded.model)
    assert len(reloaded_registry.all_ventilation_openings) == 1
    assert len(reloaded_registry.all_water_branches) == 1
    assert len(reloaded_registry.all_heating_zones) == 1


def test_complete_gui_imports_without_creating_a_window():
    from lat_ces.gui_complete import CompleteBuildingWorkspaceApp
    assert CompleteBuildingWorkspaceApp.__name__ == "CompleteBuildingWorkspaceApp"
