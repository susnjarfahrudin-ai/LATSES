"""Executable reference-house fixture for BuildingModel visualization/MEP smoke tests.

This is a visualization/integration fixture, not a final engineering design.
The canonical BuildingModel owns the two storeys and envelope; the existing
BuildingConcept adapter carries the hidden monopitch roof metadata because the
current core BuildingModel does not yet own a RoofModel field.
"""
from __future__ import annotations

from lat_ces.building.mep import (
    UnderfloorHeatingCircuit,
    UnderfloorHeatingSystem,
    VentilationOpening,
    ensure_mep_registry,
)
from lat_ces.building.model import (
    BuildingModel as CanonicalBuildingModel,
    Level as CanonicalLevel,
    Material as CanonicalMaterial,
    Room as CanonicalRoom,
)
from lat_ces.building.floor_plan import (
    FloorPlan as CanonicalFloorPlan,
    Point2D,
    Segment2D,
    Wall as CanonicalWall,
)
from lat_ces.building.geometry import Box3D, Point3D
from lat_ces.building_model.concept import (
    BuildingConcept,
    RoofCover,
    RoofCoverSpec,
    RoofModel,
    RoofShape,
    RoofStructure,
    RoofSubstructure,
    RoofSupport,
)
from lat_ces.building_model.concept_adapter import to_concept
from lat_ces.building_model.core import BuildingModel, Level, Material, Room, Wall


HOUSE_LENGTH_M = 11.5
HOUSE_WIDTH_M = 8.0
LEVEL_HEIGHT_M = 2.80


def _level(level_id: str, name: str) -> Level:
    level = Level(
        id=level_id,
        name=name,
        length_m=HOUSE_LENGTH_M,
        width_m=HOUSE_WIDTH_M,
        height_m=LEVEL_HEIGHT_M,
    )
    room_id = f"{level_id}-open-zone"
    level.add_room(Room(room_id, f"{name} open zone", HOUSE_LENGTH_M, HOUSE_WIDTH_M, LEVEL_HEIGHT_M))
    wall_material = Material("masonry envelope", density_kg_m3=1800.0, conductivity_w_mk=0.70)
    level.add_wall(Wall(f"{level_id}-north", HOUSE_LENGTH_M, 0.25, LEVEL_HEIGHT_M, wall_material, exterior=True, load_bearing=True))
    level.add_wall(Wall(f"{level_id}-south", HOUSE_LENGTH_M, 0.25, LEVEL_HEIGHT_M, wall_material, exterior=True, load_bearing=True))
    level.add_wall(Wall(f"{level_id}-east", HOUSE_WIDTH_M, 0.25, LEVEL_HEIGHT_M, wall_material, exterior=True, load_bearing=True))
    level.add_wall(Wall(f"{level_id}-west", HOUSE_WIDTH_M, 0.25, LEVEL_HEIGHT_M, wall_material, exterior=True, load_bearing=True))
    return level


def _add_mep(model: object) -> None:
    mep = ensure_mep_registry(model)
def build_test_house() -> tuple[BuildingModel, BuildingConcept]:
    model = BuildingModel(name="Reference House 11.5 x 8 m")
    model.materials["masonry"] = Material("masonry envelope", density_kg_m3=1800.0, conductivity_w_mk=0.70)
    model.add_level(_level("ground", "Prizemlje"))
    model.add_level(_level("floor1", "Sprat"))

    mep = ensure_mep_registry(model)

    # Visualization fixture: 100 mm branches at 1 m/s. This is deliberately
    # explicit so CFD/flow adapters can consume real opening identities.
    for level_id in ("ground", "floor1"):
        room_id = f"{level_id}-open-zone"
        for index in range(8):
            x = 0.8 + (index % 4) * 3.2
            y = 1.0 + (index // 4) * 5.0
            mep.add_ventilation_opening(
                VentilationOpening(
                    id=f"{level_id}-supply-{index+1}",
                    room_id=room_id,
                    kind="supply",
                    diameter_m=0.10,
                    design_velocity_m_s=1.0,
                    elevation_m=0.70,
                    x_m=x,
                    y_m=y,
                )
            )
            mep.add_ventilation_opening(
                VentilationOpening(
                    id=f"{level_id}-extract-{index+1}",
                    room_id=room_id,
                    kind="extract",
                    diameter_m=0.10,
                    design_velocity_m_s=1.0,
                    elevation_m=2.30,
                    x_m=x,
                    y_m=y,
                )
            )

        mep.add_underfloor_system(
            UnderfloorHeatingSystem(
                id=f"{level_id}-UFH",
                room_id=room_id,
                level_id=level_id,
                pipe_product_id="TEST-UFH-PIPE-16MM",
                pipe_spacing_m=0.15,
                target_indoor_temp_c=20.0,
                design_supply_temp_c=35.0,
                design_return_temp_c=30.0,
                source_type="heat_pump_air_water",
            )
        )
        mep.add_underfloor_circuit(
            UnderfloorHeatingCircuit(
                id=f"{level_id}-UFH-C1",
                room_id=room_id,
                level_id=level_id,
                pipe_product_id="TEST-UFH-PIPE-16MM",
                spacing_m=0.15,
                length_m=HOUSE_LENGTH_M * HOUSE_WIDTH_M / 0.15,
                design_supply_temp_c=35.0,
                design_return_temp_c=30.0,
            )
        )


def build_test_house() -> tuple[BuildingModel, BuildingConcept]:
    model = BuildingModel(name="Reference House 11.5 x 8 m")
    model.materials["masonry"] = Material("masonry envelope", density_kg_m3=1800.0, conductivity_w_mk=0.70)
    model.add_level(_level("ground", "Prizemlje"))
    model.add_level(_level("floor1", "Sprat"))

    _add_mep(model)

    # The current canonical BuildingModel -> Concept adapter preserves the
    # building identity. Roof metadata is attached at the concept boundary,
    # where RoofModel is already a first-class canonical concept type.
    concept = to_concept(model)
    concept.roof = RoofModel(
        length_m=HOUSE_LENGTH_M,
        width_m=HOUSE_WIDTH_M,
        shape=RoofShape.HIDDEN_MONOPITCH,
        support=RoofSupport.MASONRY_RING_BEAM,
        structure=RoofStructure.TIMBER_BEAMS,
        substructure=RoofSubstructure.BATTENS,
        cover=RoofCoverSpec(cover=RoofCover.SHEET_METAL),
        pitch_deg=12.0,
        overhang_m=0.25,
    )
    return model, concept


def build_test_workflow_house() -> CanonicalBuildingModel:
    """Build the same reference house on the production GUI BuildingModel.

    The engineering-report path consumes this model, whose geometry contract
    is Level.floor_plan -> FloorPlan.walls.
    """
    model = CanonicalBuildingModel(name="Reference House 11.5 x 8 m")
    model.add_material(
        CanonicalMaterial(
            name="masonry envelope",
            density=1800.0,
            thermal_conductivity=0.70,
            material_id="masonry",
        )
    )

    for level_id, name, elevation in (
        ("ground", "Prizemlje", 0.0),
        ("floor1", "Sprat", LEVEL_HEIGHT_M),
    ):
        level = CanonicalLevel(
            name=name,
            elevation=elevation,
            height=LEVEL_HEIGHT_M,
            level_id=level_id,
            length_m=HOUSE_LENGTH_M,
            width_m=HOUSE_WIDTH_M,
        )
        room_id = f"{level_id}-open-zone"
        level.add_room(
            CanonicalRoom(
                name=f"{name} open zone",
                footprint=Box3D(Point3D(0.0, 0.0, 0.0), HOUSE_LENGTH_M, HOUSE_WIDTH_M, LEVEL_HEIGHT_M),
                room_id=room_id,
            )
        )

        plan = CanonicalFloorPlan(name=f"{name} floor plan")
        walls = (
            ("north", Point2D(0.0, 0.0), Point2D(HOUSE_LENGTH_M, 0.0), 4.0),
            ("south", Point2D(0.0, HOUSE_WIDTH_M), Point2D(HOUSE_LENGTH_M, HOUSE_WIDTH_M), 4.0),
            ("east", Point2D(HOUSE_LENGTH_M, 0.0), Point2D(HOUSE_LENGTH_M, HOUSE_WIDTH_M), 2.0),
            ("west", Point2D(0.0, 0.0), Point2D(0.0, HOUSE_WIDTH_M), 2.0),
        )
        for wall_name, start, end, tributary_width in walls:
            plan.add_wall(
                CanonicalWall(
                    name=f"{level_id}-{wall_name}",
                    segment=Segment2D(start, end),
                    thickness=0.25,
                    load_bearing=True,
                    material_id="masonry",
                    tributary_width_m=tributary_width,
                    exterior=True,
                    room_ids=(room_id,),
                )
            )
        level.set_floor_plan(plan)
        model.add_level(level)

    _add_mep(model)
    return model


def fixture_summary() -> dict[str, object]:
    model, concept = build_test_house()
    mep = ensure_mep_registry(model)
    return {
        "name": model.name,
        "footprint_m": [HOUSE_LENGTH_M, HOUSE_WIDTH_M],
        "levels": list(model.levels),
        "two_intermediate_slab_boundaries": ["ground/floor1", "floor1/roof"],
        "roof": concept.roof.shape.value if concept.roof else None,
        "roof_cover": concept.roof.cover.cover.value if concept.roof else None,
        "heating_source": "heat_pump_air_water",
        "underfloor_systems": len(mep.all_underfloor_systems),
        "underfloor_circuits": len(mep.all_underfloor_circuits),
        "ventilation_openings": len(mep.all_ventilation_openings),
        "ventilation_supply_openings": sum(o.kind == "supply" for o in mep.all_ventilation_openings),
        "ventilation_extract_openings": sum(o.kind == "extract" for o in mep.all_ventilation_openings),
    }


if __name__ == "__main__":
    from pprint import pprint

    pprint(fixture_summary())
