"""Editable reference-house project adapter."""
from __future__ import annotations

from math import sqrt

from lat_ces.reference_house import ReferenceHouse
from .electrical import ElectricalLoad, ensure_electrical_registry
from .geometry import Box3D, Point3D
from .mep import ensure_mep_registry
from .model import BuildingModel, Level, Material, Roof, Room
from .orientation import BuildingOrientation
from .project_spec import BuildingProjectSpec, JoinerySpec, LevelProjectSpec, RoomSpec, WallConstructionSpec
from lat_ces.building_model.systems import HeatingZone, VentilationOpening, WaterBranch
from .workflow import BuildingWorkflow, make_envelope_floor_plan


def _room_spec(room: dict) -> RoomSpec:
    area = max(0.01, float(room.get("area_m2", 0.0)))
    length = sqrt(area)
    width = area / length
    return RoomSpec(name=str(room.get("name", "Prostorija")), length_m=length, width_m=width, role=str(room.get("orientation", "room")))


def _add_reference_rooms(level: Level, room_data: list[dict]) -> None:
    """Materialize reference-room area/volume into the canonical BuildingModel."""
    y = 0.0
    for data in room_data:
        height = float(data.get("height_m", level.height))
        area = float(data.get("area_m2", 0.0))
        if height <= 0.0 or area <= 0.0:
            continue
        length = level.length_m
        width = area / length
        if y + width > level.width_m + 1e-9:
            raise ValueError(f"Reference room areas exceed level envelope for {level.name}: {y + width:.6g} m > {level.width_m:.6g} m")
        level.add_room(Room(name=str(data.get("name", "Prostorija")), footprint=Box3D(origin=Point3D(0.0, y, level.elevation), length=length, width=width, height=height)))
        y += width


def _canonical_room_map(workflow: BuildingWorkflow, data: dict) -> dict[str, Room]:
    """Map reference-house room ids to the actual canonical Room objects."""
    mapping: dict[str, Room] = {}
    for level_data, level in zip(data["levels"], workflow.model.levels.values()):
        actual_rooms = iter(level.rooms.values())
        for room_data in level_data.get("rooms", []):
            if float(room_data.get("height_m", 0.0)) <= 0.0:
                continue
            mapping[str(room_data["id"])] = next(actual_rooms)
    return mapping


def _populate_reference_materials(model: BuildingModel) -> tuple[str, str]:
    """Register explicit material properties required by the smoke-test solvers.

    The source house gives material families, not verified manufacturer datasets.
    These values are therefore explicit engineering-test assumptions, not claims
    about a specific product.
    """
    masonry = model.add_material(Material(name="250×200×250 mm family — smoke-test assumption", density=900.0, thermal_conductivity=0.25))
    insulation = model.add_material(Material(name="kamena vuna", density=120.0, thermal_conductivity=0.036))
    model.add_material(Material(name="vapneno-cementni malter", density=1800.0, thermal_conductivity=0.70))
    return masonry.material_id, insulation.material_id


def _activate_structural_envelope(level: Level, wall_material_id: str) -> None:
    """Mark the generated envelope walls as preliminary load-bearing test inputs."""
    if level.floor_plan is None:
        return
    for wall in level.floor_plan.walls.values():
        wall.load_bearing = True
        wall.material_id = wall_material_id
        wall.tributary_width_m = 2.0


def _populate_reference_engineering_inputs(workflow: BuildingWorkflow, data: dict) -> None:
    """Populate canonical MEP/electrical design inputs for the engineering smoke test."""
    registry = ensure_mep_registry(workflow.model)
    room_map = _canonical_room_map(workflow, data)

    ventilation_rooms = ["P-LIV", "P-KIT", "P-OFF", "P-GUEST", "S1-MASTER", "S1-STUDY", "S2-STUDIO", "S2-GUEST", "S2-LOUNGE", "S2-GYM"]
    for index, source_room_id in enumerate(ventilation_rooms):
        kind = "supply" if index < 5 else "extract"
        registry.add_ventilation_opening(VentilationOpening(id=f"VO-{index + 1:02d}", room_id=room_map[source_room_id].room_id, kind=kind, diameter_m=0.25, design_velocity_m_s=0.50, elevation_m=0.70 if kind == "supply" else 2.40, x_m=1.0, y_m=1.0 + index))

    for index, source_room_id in enumerate(["P-KIT", "P-BTH", "S1-BTH", "S2-BTH"]):
        room_id = room_map[source_room_id].room_id
        registry.add_water_branch(WaterBranch(id=f"CW-{index + 1:02d}", room_id=room_id, service="cold_water", diameter_m=0.020, design_flow_m3_s=0.00020, length_m=5.0 + index, x1_m=0.0, y1_m=float(index), x2_m=5.0, y2_m=float(index)))
        registry.add_water_branch(WaterBranch(id=f"DR-{index + 1:02d}", room_id=room_id, service="drain", diameter_m=0.050, design_flow_m3_s=0.00050, length_m=4.0 + index, x1_m=5.0, y1_m=float(index), x2_m=9.0, y2_m=float(index)))

    room_data_by_id = {room["id"]: room for level in data["levels"] for room in level.get("rooms", [])}
    for circuit in data["heating"]["circuits"]:
        for source_room_id in circuit["rooms"]:
            room = room_data_by_id[source_room_id]
            load_w = float(room["area_m2"]) * float(circuit["design_w_per_m2"])
            registry.add_heating_zone(HeatingZone(id=f"{circuit['id']}-{source_room_id}", room_id=room_map[source_room_id].room_id, emitter_type=str(circuit["type"]), design_supply_temp_c=float(circuit["supply_c"]), design_return_temp_c=float(circuit["return_c"]), target_indoor_temp_c=20.0, room_heat_load_w=load_w))

    electrical = ensure_electrical_registry(workflow.model)
    lighting = data["lighting"]
    for level in data["levels"]:
        for room in level.get("rooms", []):
            if float(room.get("height_m", 0.0)) <= 0.0:
                continue
            name = str(room["name"])
            if name in {"Radna soba", "Studio / biblioteka"}: lux = float(lighting["work_target_lux"])
            elif "Kupatilo" in name: lux = float(lighting["bath_target_lux"])
            elif "Kuhinja" in name: lux = float(lighting["kitchen_target_lux"])
            elif any(value in name for value in ("Spavaća", "Roditeljska", "Gostinska")): lux = float(lighting["bedroom_target_lux"])
            else: lux = float(lighting["living_target_lux"])
            actual_id = room_map[room["id"]].room_id
            electrical.add(ElectricalLoad(name=f"Rasvjeta — {name}", kind="lighting", room_id=actual_id, power_w=float(room["area_m2"]) * lux * 0.008, demand_factor=1.0))
            electrical.add(ElectricalLoad(name=f"Utičnice — {name}", kind="socket", room_id=actual_id, power_w=500.0, quantity=2, demand_factor=0.40))


def build_reference_house_workflow() -> BuildingWorkflow:
    house = ReferenceHouse.default()
    data = house.data
    dimensions = data["dimensions"]
    orientation = BuildingOrientation()
    model = BuildingModel(name=str(data["name"]), model_id=str(data["model_id"]), orientation=orientation)
    masonry_material_id, _ = _populate_reference_materials(model)
    envelope = data.get("envelope", {})
    wall = envelope.get("exterior_wall", {})
    wall_construction = WallConstructionSpec(block_brand=str(wall.get("masonry_block", "")), wall_thickness_m=0.25, insulation_type=str(wall.get("insulation", "")), insulation_thickness_m=float(wall.get("insulation_thickness_m", 0.0)), exterior_cladding=str(wall.get("facade_finish", "")), interior_cladding=str(wall.get("interior_finish", "")), render_thickness_m=float(wall.get("interior_finish_thickness_m", 0.0)))
    project = BuildingProjectSpec(name=str(data["name"]), floor_count=len(data["levels"]), floor_count_finalized=True, roof_shape=str(data["roof"]["type"]), roof_height_m=0.0, orientation=orientation)
    project.roof.roof_type = str(data["roof"]["type"])
    project.roof.length_m = float(dimensions["length_m"])
    project.roof.width_m = float(dimensions["width_m"])
    project.roof.slope_deg = float(data["roof"].get("slope_deg", 0.0))
    project.roof.covering = str(data["roof"].get("covering", ""))
    project.roof.construction = "Drvena krovna građa"
    project.roof.height_m = 0.0
    for level_data in data["levels"]:
        rooms = [_room_spec(room) for room in level_data.get("rooms", [])]
        joinery = data.get("joinery", {})
        project.levels.append(LevelProjectSpec(name=str(level_data["name"]), height_m=float(dimensions["level_height_m"]), length_m=float(dimensions["length_m"]), width_m=float(dimensions["width_m"]), construction=wall_construction, cladding=str(wall.get("facade_finish", "")), joinery=JoinerySpec(material=str(joinery.get("default_frame", "")), glazing="3 stakla / argon / Low-E / warm edge", frame_type=str(joinery.get("default_frame", "")), thermal_transmittance_w_m2k=0.7, opening_count=0), rooms=rooms, finalized=False))
    workflow = BuildingWorkflow(model=model, project_spec=project, current_step=3)
    previous = None
    for level_data in data["levels"]:
        joinery = data.get("joinery", {})
        level = model.add_level(Level(name=str(level_data["name"]), elevation=0.0 if previous is None else previous.top_elevation, height=float(dimensions["level_height_m"]), length_m=float(dimensions["length_m"]), width_m=float(dimensions["width_m"]), wall_construction=str(wall.get("masonry_block", "")), insulation=str(wall.get("insulation", "")), cladding=str(wall.get("facade_finish", "")), joinery=str(joinery.get("default_frame", "")), facade_finish=str(wall.get("facade_finish", "")), insulation_material=str(wall.get("insulation", "")), insulation_thickness_m=float(wall.get("insulation_thickness_m", 0.0)), interior_plaster_material=str(wall.get("interior_finish", "")), interior_plaster_thickness_m=float(wall.get("interior_finish_thickness_m", 0.0)), dead_load_kpa=float(level_data.get("loads", {}).get("dead_kpa", 0.0)), live_load_kpa=float(level_data.get("loads", {}).get("live_kpa", 0.0))))
        level.set_floor_plan(make_envelope_floor_plan(level.name, level.length_m, level.width_m, 0.25))
        _activate_structural_envelope(level, masonry_material_id)
        _add_reference_rooms(level, level_data.get("rooms", []))
        previous = level
    roof_data = data["roof"]
    model.set_roof(Roof(roof_type=str(roof_data["type"]), construction="Drvena krovna građa", covering=str(roof_data.get("covering", "")), substructure=f"Rog {roof_data.get('rafter_section_mm', [100, 200])[0]}×{roof_data.get('rafter_section_mm', [100, 200])[1]} mm", support=str(roof_data.get("ridge_direction", "")), length_m=float(dimensions["length_m"]), width_m=float(dimensions["width_m"]), slope_deg=float(roof_data.get("slope_deg", 0.0)), height_m=0.0))
    _populate_reference_engineering_inputs(workflow, data)
    workflow.active_level_id = next(iter(model.levels), None)
    return workflow


__all__ = ["build_reference_house_workflow"]