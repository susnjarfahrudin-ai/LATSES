"""Deterministic reference-house calculations for the LAT-CES showcase."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from math import cos, radians
from typing import Any


@dataclass(frozen=True)
class HeatingCircuitResult:
    circuit_id: str
    type: str
    heat_load_w: float
    mass_flow_kg_s: float
    delta_t_k: float
    rooms: tuple[str, ...]


@dataclass(frozen=True)
class HouseSummary:
    floor_area_m2: float
    volume_m3: float
    roof_area_m2: float
    wall_area_m2: float
    blocks: float
    slab_concrete_m3: float
    heating_load_w: float
    heating_mass_flow_kg_s: float
    ventilation_m3_h: float
    lighting_w: float
    gross_floor_area_m2: float = 0.0
    conditioned_floor_area_m2: float = 0.0


class ReferenceHouse:
    WATER_CP_J_KG_K = 4180.0
    SLAB_M = 0.20
    PERIMETER_M = 44.0
    OPENING_RATIO = 0.16
    BLOCK_FACE_M2 = 0.25 * 0.20

    def __init__(self, data: dict[str, Any]):
        self.data = data

    @classmethod
    def default(cls) -> "ReferenceHouse":
        """Load the reference model reliably in source, editable and packaged builds."""
        resource_path = Path(__file__).with_name("reference_house_model.json")
        raw = resource_path.read_text(encoding="utf-8")
        return cls(json.loads(raw))

    @property
    def levels(self):
        return self.data["levels"]

    @property
    def rooms(self):
        return [r for level in self.levels for r in level["rooms"]]

    @property
    def conditioned_rooms(self):
        return [r for r in self.rooms if r["height_m"] > 0]

    @property
    def conditioned_floor_area_m2(self) -> float:
        """Area explicitly represented by conditioned rooms; currently 338 m²."""
        return sum(r["area_m2"] for r in self.conditioned_rooms)

    @property
    def floor_area_m2(self) -> float:
        """Backward-compatible alias for conditioned floor area."""
        return self.conditioned_floor_area_m2

    @property
    def gross_floor_area_m2(self) -> float:
        """Geometric gross floor area from the footprint and number of levels."""
        d = self.data["dimensions"]
        level_area = d.get("gross_level_area_m2", d["length_m"] * d["width_m"])
        return level_area * len(self.levels)

    @property
    def volume_m3(self):
        return sum(r["area_m2"] * r["height_m"] for r in self.conditioned_rooms)

    @property
    def roof_area_m2(self):
        d = self.data["dimensions"]
        roof = self.data["roof"]
        slope = radians(roof["slope_deg"])
        rafter = (d["width_m"] / 2.0) / cos(slope) + roof["eave_overhang_m"]
        return 2.0 * (d["length_m"] + 2.0 * roof["eave_overhang_m"]) * rafter * (1.0 + self.data["quantities"]["roof_cover_waste_factor"])

    @property
    def wall_area_m2(self):
        gross = self.PERIMETER_M * self.data["dimensions"]["level_height_m"] * len(self.levels)
        return gross * (1.0 - self.OPENING_RATIO)

    def estimate_blocks(self):
        return self.wall_area_m2 / self.BLOCK_FACE_M2 * (1.0 + self.data["quantities"]["block_waste_factor"])

    def slab_concrete_m3(self):
        d = self.data["dimensions"]
        return d["length_m"] * d["width_m"] * self.SLAB_M * len(self.levels)

    def heating_circuits(self):
        rooms = {r["id"]: r for r in self.rooms}
        result = []
        for c in self.data["heating"]["circuits"]:
            load = sum(rooms[r]["area_m2"] for r in c["rooms"]) * c["design_w_per_m2"]
            dt = c["supply_c"] - c["return_c"]
            result.append(HeatingCircuitResult(c["id"], c["type"], load, load / (self.WATER_CP_J_KG_K * dt), dt, tuple(c["rooms"])))
        return tuple(result)

    def heating_load_w(self):
        return sum(x.heat_load_w for x in self.heating_circuits())

    def heating_mass_flow_kg_s(self):
        return sum(x.mass_flow_kg_s for x in self.heating_circuits())

    def ventilation_m3_h(self):
        return self.volume_m3 * self.data["ventilation"]["target_ach"]

    def lighting_w(self):
        t = self.data["lighting"]
        total = 0.0
        for r in self.conditioned_rooms:
            if r["name"] in {"Radna soba", "Studio / biblioteka"}:
                lux = t["work_target_lux"]
            elif "Kupatilo" in r["name"]:
                lux = t["bath_target_lux"]
            elif "Kuhinja" in r["name"]:
                lux = t["kitchen_target_lux"]
            elif any(x in r["name"] for x in ("Spavaća", "Roditeljska", "Gostinska")):
                lux = t["bedroom_target_lux"]
            else:
                lux = t["living_target_lux"]
            total += r["area_m2"] * lux * 0.008
        return total

    def envelope_scenarios(self):
        # Comparative only: explicit assumed layer conductivities; not a code check.
        scenarios = (("Vuna 12 cm", 0.12, 0.036), ("Vuna 16 cm", 0.16, 0.036), ("Vuna 20 cm", 0.20, 0.036), ("EPS 16 cm", 0.16, 0.036))
        results = []
        for name, thickness, lam in scenarios:
            r_layer = thickness / lam
            r_total = 0.13 + r_layer + 0.04
            results.append({"name": name, "thickness_m": thickness, "r_m2k_w": r_total, "u_w_m2k": 1.0 / r_total})
        return tuple(results)

    def glazing_scenarios(self):
        # Placeholder comparative values are configuration inputs, not manufacturer data.
        return (("2 stakla", 2, 2.7), ("3 stakla Low-E", 3, 0.9), ("3 stakla Low-E + warm edge", 3, 0.7))

    def summary(self):
        return HouseSummary(
            floor_area_m2=self.floor_area_m2,
            volume_m3=self.volume_m3,
            roof_area_m2=self.roof_area_m2,
            wall_area_m2=self.wall_area_m2,
            blocks=self.estimate_blocks(),
            slab_concrete_m3=self.slab_concrete_m3(),
            heating_load_w=self.heating_load_w(),
            heating_mass_flow_kg_s=self.heating_mass_flow_kg_s(),
            ventilation_m3_h=self.ventilation_m3_h(),
            lighting_w=self.lighting_w(),
            gross_floor_area_m2=self.gross_floor_area_m2,
            conditioned_floor_area_m2=self.conditioned_floor_area_m2,
        )

    def simulation_guidance(self, air_velocity_m_s: float) -> str:
        if air_velocity_m_s < 0.10:
            return "Vrlo blago strujanje — uglavnom izvan zone izraženog propuha."
        if air_velocity_m_s < 0.20:
            return "Umjereno strujanje — provjeriti položaj usisa/izduva i osjećaj korisnika."
        return "Visoko strujanje — vjerovatna osjetljivost na propuh; potrebno je prilagoditi geometriju ili protok."


__all__ = ["HeatingCircuitResult", "HouseSummary", "ReferenceHouse"]
