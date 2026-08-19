"""JSON persistence for the canonical BuildingModel workflow."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .floor_plan import FloorPlan, Opening, Point2D, Segment2D, Wall
from .model import BuildingModel, Level, Material, Roof
from .orientation import BuildingOrientation
from .project_spec import BuildingProjectSpec, LevelProjectSpec, RoomSpec, WallConstructionSpec, JoinerySpec, RoofSpec
from .workflow import BuildingWorkflow
from .mep import ensure_mep_registry
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch


def _plan_to_dict(plan: FloorPlan) -> dict[str, object]:
    return {"name": plan.name, "plan_id": plan.plan_id, "walls": [{
        "name": wall.name, "wall_id": wall.wall_id, "thickness": wall.thickness,
        "load_bearing": wall.load_bearing, "material_id": wall.material_id,
        "tributary_width_m": wall.tributary_width_m,
        "start": {"x": wall.segment.start.x, "y": wall.segment.start.y},
        "end": {"x": wall.segment.end.x, "y": wall.segment.end.y},
        "openings": [asdict(opening) for opening in wall.openings],
    } for wall in plan.walls.values()]}


def _plan_from_dict(data: dict[str, object]) -> FloorPlan:
    plan = FloorPlan(name=str(data.get("name", "Etaža")))
    for item in data.get("walls", []):
        wall_data = dict(item); start, end = dict(wall_data["start"]), dict(wall_data["end"])
        wall = Wall(
            name=str(wall_data.get("name", "Zid")),
            segment=Segment2D(Point2D(float(start["x"]), float(start["y"])), Point2D(float(end["x"]), float(end["y"]))),
            thickness=float(wall_data.get("thickness", 0.20)),
            load_bearing=bool(wall_data.get("load_bearing", False)),
            material_id=str(wall_data["material_id"]) if wall_data.get("material_id") else None,
            tributary_width_m=float(wall_data.get("tributary_width_m", 0.0)),
        )
        for opening_data in wall_data.get("openings", []):
            wall.add_opening(Opening(kind=str(opening_data["kind"]), offset=float(opening_data["offset"]), width=float(opening_data["width"]), height_m=float(opening_data.get("height_m", 2.10))))
        plan.add_wall(wall)
    return plan


def _spec_to_dict(spec: BuildingProjectSpec | None) -> dict[str, object] | None:
    return asdict(spec) if spec else None


def _spec_from_dict(data: dict[str, object] | None, name: str, *, fallback_orientation: BuildingOrientation | None = None) -> BuildingProjectSpec:
    if not data:
        return BuildingProjectSpec(name=name, orientation=fallback_orientation or BuildingOrientation())
    roof_data = dict(data.get("roof", {})); orientation_data = dict(data.get("orientation", {}))
    project = BuildingProjectSpec(name=str(data.get("name", name)), floor_count=int(data.get("floor_count", 0)), floor_count_finalized=bool(data.get("floor_count_finalized", False)), roof_shape=str(data.get("roof_shape", "Nije definisan")), roof_height_m=float(data.get("roof_height_m", 0.0)), roof=RoofSpec(**roof_data) if roof_data else RoofSpec(roof_type=str(data.get("roof_shape", "Nije definisan")), height_m=float(data.get("roof_height_m", 0.0))), orientation=BuildingOrientation(**orientation_data) if orientation_data else (fallback_orientation or BuildingOrientation()))
    for level_data in data.get("levels", []):
        item = dict(level_data); construction = WallConstructionSpec(**dict(item.get("construction", {}))); joinery = JoinerySpec(**dict(item.get("joinery", {}))); rooms = [RoomSpec(**dict(room)) for room in item.get("rooms", [])]
        project.levels.append(LevelProjectSpec(name=str(item.get("name", "Etaža")), height_m=float(item.get("height_m", 2.80)), length_m=float(item.get("length_m", 0.0)), width_m=float(item.get("width_m", 0.0)), construction=construction, cladding=str(item.get("cladding", "")), joinery=joinery, rooms=rooms, finalized=bool(item.get("finalized", False))))
    return project


def _mep_to_dict(model: BuildingModel):
    registry = getattr(model, "mep", None)
    if registry is None: return None
    return {"ventilation_openings": [asdict(x) for x in registry.all_ventilation_openings], "water_branches": [asdict(x) for x in registry.all_water_branches], "heating_zones": [asdict(x) for x in registry.all_heating_zones]}


def _mep_from_dict(model: BuildingModel, data):
    if not data: return
    registry = ensure_mep_registry(model)
    for item in data.get("ventilation_openings", []): registry.add_ventilation_opening(VentilationOpening(**dict(item)))
    for item in data.get("water_branches", []): registry.add_water_branch(WaterBranch(**dict(item)))
    for item in data.get("heating_zones", []): registry.add_heating_zone(HeatingZone(**dict(item)))


def workflow_to_dict(workflow: BuildingWorkflow) -> dict[str, object]:
    project_spec = workflow.project_spec
    if project_spec is not None: project_spec.orientation = workflow.model.orientation
    return {"schema": "LAT-CES-BUILDING-7", "model": {
        "name": workflow.model.name, "model_id": workflow.model.model_id,
        "orientation": asdict(workflow.model.orientation), "roof": asdict(workflow.model.roof) if workflow.model.roof else None,
        "materials": [asdict(m) for m in workflow.model.materials.values()],
        "levels": [{"name": level.name, "level_id": level.level_id, "elevation": level.elevation, "height": level.height, "length_m": level.length_m, "width_m": level.width_m, "wall_construction": level.wall_construction, "insulation": level.insulation, "cladding": level.cladding, "joinery": level.joinery, "facade_finish": level.facade_finish, "insulation_material": level.insulation_material, "insulation_thickness_m": level.insulation_thickness_m, "interior_plaster_material": level.interior_plaster_material, "interior_plaster_thickness_m": level.interior_plaster_thickness_m, "dead_load_kpa": level.dead_load_kpa, "live_load_kpa": level.live_load_kpa, "floor_plan": _plan_to_dict(level.floor_plan) if level.floor_plan else None} for level in workflow.model.levels.values()],
        "mep": _mep_to_dict(workflow.model)}, "project_spec": _spec_to_dict(project_spec), "roof_shape": workflow.roof_shape, "roof_height_m": workflow.roof_height_m, "current_step": workflow.current_step, "active_level_id": workflow.active_level_id}


def save_workflow(workflow: BuildingWorkflow, path: str | Path) -> Path:
    target = Path(path); target.write_text(json.dumps(workflow_to_dict(workflow), indent=2, ensure_ascii=False), encoding="utf-8"); return target


def load_workflow(path: str | Path) -> BuildingWorkflow:
    data = json.loads(Path(path).read_text(encoding="utf-8")); model_data = dict(data["model"]); orientation_data = model_data.get("orientation")
    model = BuildingModel(name=str(model_data.get("name", "Novi objekat")), orientation=BuildingOrientation(**dict(orientation_data)) if orientation_data else BuildingOrientation())
    roof_data = model_data.get("roof")
    if roof_data: model.set_roof(Roof(**dict(roof_data)))
    for material_data in model_data.get("materials", []):
        model.add_material(Material(**dict(material_data)))
    workflow = BuildingWorkflow(model=model, current_step=int(data.get("current_step", 1)))
    workflow.project_spec = _spec_from_dict(data.get("project_spec"), model.name, fallback_orientation=model.orientation); workflow.project_spec.orientation = model.orientation
    workflow.roof_shape = str(data.get("roof_shape", workflow.project_spec.roof_shape)); workflow.roof_height_m = float(data.get("roof_height_m", workflow.project_spec.roof_height_m))
    for level_data in model_data.get("levels", []):
        item = dict(level_data); level = model.add_level(Level(name=str(item["name"]), elevation=float(item["elevation"]), height=float(item["height"]), length_m=float(item.get("length_m", 0.0)), width_m=float(item.get("width_m", 0.0)), wall_construction=str(item.get("wall_construction", "")), insulation=str(item.get("insulation", "")), cladding=str(item.get("cladding", "")), joinery=str(item.get("joinery", "")), facade_finish=str(item.get("facade_finish", "")), insulation_material=str(item.get("insulation_material", "")), insulation_thickness_m=float(item.get("insulation_thickness_m", 0.0)), interior_plaster_material=str(item.get("interior_plaster_material", "")), interior_plaster_thickness_m=float(item.get("interior_plaster_thickness_m", 0.0)), dead_load_kpa=float(item.get("dead_load_kpa", 0.0)), live_load_kpa=float(item.get("live_load_kpa", 0.0))))
        if item.get("floor_plan"): level.set_floor_plan(_plan_from_dict(dict(item["floor_plan"])))
    _mep_from_dict(model, model_data.get("mep"))
    active = data.get("active_level_id")
    if active and active in model.levels: workflow.active_level_id = str(active)
    elif model.levels: workflow.active_level_id = next(iter(model.levels))
    return workflow
