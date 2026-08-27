# -*- coding: utf-8 -*-
"""LAT-CES standalone master test runtime.

Combined from the two supplied text parts for the isolated fahro-test project.
This file is intentionally independent from the production LAT-CES GUI/runtime.
It provides the hardened scientific core, thermo/fluid/domain extensions,
geotechnical/material matrix, TCP telemetry, standalone PyQt6 dashboard and
PDF reporter used for the EXE experiment.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import socket
import sys
import threading
import time
from collections import deque
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from PyQt6 import QtCore, QtWidgets
import pyqtgraph as pg

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ============================================================================
# TITLE I: CONSTITUTIONAL CORE
# ============================================================================

class LATCESException(Exception):
    pass


class ImmutableObjectError(LATCESException):
    pass


class InvalidLifecycleTransition(LATCESException):
    pass


class DimensionError(LATCESException):
    pass


class IntegrityViolationError(LATCESException):
    pass


class AuthorityEscalationError(LATCESException):
    pass


class SafetyBoundaryViolation(LATCESException):
    pass


class LifecycleState(Enum):
    DRAFT = "DRAFT"
    REVIEWED = "REVIEWED"
    VERIFIED = "VERIFIED"
    VALIDATED = "VALIDATED"
    RELEASED = "RELEASED"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    RETIRED = "RETIRED"


class HardenedSKO:
    VALID_TRANSITIONS = {
        LifecycleState.DRAFT: [LifecycleState.REVIEWED],
        LifecycleState.REVIEWED: [LifecycleState.VERIFIED],
        LifecycleState.VERIFIED: [LifecycleState.VALIDATED],
        LifecycleState.VALIDATED: [LifecycleState.RELEASED],
        LifecycleState.RELEASED: [LifecycleState.DEPRECATED],
        LifecycleState.DEPRECATED: [LifecycleState.ARCHIVED],
        LifecycleState.ARCHIVED: [LifecycleState.RETIRED],
        LifecycleState.RETIRED: [],
    }

    def __init__(
        self,
        name: str,
        object_type: str,
        definition: str,
        assumptions: List[str],
        limitations: List[str],
        creator: str,
    ):
        object.__setattr__(self, "_locked", False)
        self.sko_id = f"LAT-SKO-{object_type.upper()}-{int(time.time() * 1000)}"
        self.uuid = hashlib.sha256(
            f"{self.sko_id}-{time.time_ns()}".encode("utf-8")
        ).hexdigest()[:16]
        self.name = name
        self.object_type = object_type
        self.definition = definition
        self.assumptions = tuple(str(x) for x in assumptions)
        self.limitations = tuple(str(x) for x in limitations)
        self.creator = creator
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.lifecycle_status = LifecycleState.DRAFT
        self.previous_revision_hash = None
        self.integrity_hash = self._calculate_signature()

    def _calculate_signature(self) -> str:
        payload = {
            "sko_id": self.sko_id,
            "uuid": self.uuid,
            "name": self.name,
            "object_type": self.object_type,
            "definition": self.definition,
            "assumptions": self.assumptions,
            "limitations": self.limitations,
            "creator": self.creator,
            "created_at": self.created_at,
            "lifecycle_status": self.lifecycle_status.value,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()

    def transition(self, target_state: LifecycleState) -> None:
        if self._locked:
            raise ImmutableObjectError(
                f"Constitutional violation: {self.sko_id} is immutable"
            )
        if target_state not in self.VALID_TRANSITIONS[self.lifecycle_status]:
            raise InvalidLifecycleTransition(
                f"Illegal state hop: {self.lifecycle_status.value} -> {target_state.value}"
            )
        object.__setattr__(self, "lifecycle_status", target_state)
        if target_state is LifecycleState.RELEASED:
            object.__setattr__(self, "_locked", True)
        object.__setattr__(self, "integrity_hash", self._calculate_signature())

    def create_hardened_revision(
        self, updated_definition: str, modifications: Dict[str, Any]
    ) -> "HardenedSKO":
        if self.lifecycle_status is not LifecycleState.RELEASED:
            raise LATCESException("A hardened revision requires a RELEASED foundation")
        revision = HardenedSKO(
            self.name,
            self.object_type,
            updated_definition,
            list(modifications.get("assumptions", self.assumptions)),
            list(modifications.get("limitations", self.limitations)),
            modifications.get("creator", "LAT-SYSTEM-EVOLUTION"),
        )
        revision.previous_revision_hash = self.integrity_hash
        return revision

    def __setattr__(self, key: str, value: Any) -> None:
        if getattr(self, "_locked", False):
            raise ImmutableObjectError(
                f"Structural lock assertion: modification of '{key}' denied"
            )
        object.__setattr__(self, key, value)
        if key not in {"integrity_hash", "_locked"} and hasattr(self, "integrity_hash"):
            object.__setattr__(self, "integrity_hash", self._calculate_signature())

    def export_canonical_json(self) -> str:
        payload = {
            "sko_id": self.sko_id,
            "uuid": self.uuid,
            "name": self.name,
            "object_type": self.object_type,
            "definition": self.definition,
            "assumptions": self.assumptions,
            "limitations": self.limitations,
            "creator": self.creator,
            "created_at": self.created_at,
            "lifecycle_status": self.lifecycle_status.value,
            "previous_revision_hash": self.previous_revision_hash,
            "integrity_hash": self.integrity_hash,
        }
        return json.dumps(payload, sort_keys=True, default=str)


# ============================================================================
# TITLE II: DIMENSION, UNIT, QUANTITY AND MEASUREMENT
# ============================================================================

class HardenedDimension:
    CANONICAL_ORDER = ["M", "L", "T", "I", "Θ", "N", "J"]

    def __init__(self, name: str, vector_map: Dict[str, int]):
        if not name:
            raise DimensionError("Dimension requires an explicit name")
        cleaned = {
            key: value
            for key, value in vector_map.items()
            if key in self.CANONICAL_ORDER and value != 0
        }
        self.name = name
        self._vector = MappingProxyType(
            {key: cleaned[key] for key in self.CANONICAL_ORDER if key in cleaned}
        )
        self.canonical_descriptor = self._generate_canonical_descriptor()

    def _generate_canonical_descriptor(self) -> str:
        parts = []
        for symbol in self.CANONICAL_ORDER:
            power = self._vector.get(symbol, 0)
            if power:
                parts.append(f"{symbol}^{power}")
        return "*".join(parts) if parts else "DIMENSIONLESS"

    @property
    def vector(self):
        return self._vector

    def __mul__(self, other: "HardenedDimension") -> "HardenedDimension":
        if not isinstance(other, HardenedDimension):
            raise DimensionError("Dimension multiplication requires HardenedDimension")
        combined = {
            symbol: self._vector.get(symbol, 0) + other.vector.get(symbol, 0)
            for symbol in self.CANONICAL_ORDER
        }
        return HardenedDimension(f"({self.name}*{other.name})", combined)

    def __truediv__(self, other: "HardenedDimension") -> "HardenedDimension":
        if not isinstance(other, HardenedDimension):
            raise DimensionError("Dimension division requires HardenedDimension")
        combined = {
            symbol: self._vector.get(symbol, 0) - other.vector.get(symbol, 0)
            for symbol in self.CANONICAL_ORDER
        }
        return HardenedDimension(f"({self.name}/{other.name})", combined)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, HardenedDimension) and dict(self.vector) == dict(other.vector)

    def __str__(self) -> str:
        if not self._vector:
            return "Dimensionless [1]"
        return " ".join(
            f"{key}^{value}" if value != 1 else key
            for key, value in self._vector.items()
        )


MASS = HardenedDimension("Mass", {"M": 1})
LENGTH = HardenedDimension("Length", {"L": 1})
TIME = HardenedDimension("Time", {"T": 1})
CURRENT = HardenedDimension("Electric Current", {"I": 1})
TEMPERATURE = HardenedDimension("Temperature", {"Θ": 1})
AMOUNT = HardenedDimension("Amount of Substance", {"N": 1})
LUMINOUS_INTENSITY = HardenedDimension("Luminous Intensity", {"J": 1})
DIMENSIONLESS = HardenedDimension("Dimensionless", {})
VELOCITY = LENGTH / TIME
ACCELERATION = VELOCITY / TIME
FORCE = MASS * ACCELERATION
PRESSURE = FORCE / (LENGTH * LENGTH)
ENERGY = FORCE * LENGTH
AREA = LENGTH * LENGTH
VOLUME = AREA * LENGTH
DENSITY = MASS / VOLUME
SPECIFIC_HEAT = HardenedDimension("Specific Heat Capacity", {"L": 2, "T": -2, "Θ": -1})
THERMAL_CONDUCTIVITY = HardenedDimension(
    "Thermal Conductivity", {"M": 1, "L": 1, "T": -3, "Θ": -1}
)
DYNAMIC_VISCOSITY = HardenedDimension(
    "Dynamic Viscosity", {"M": 1, "L": -1, "T": -1}
)


class HardenedUnit(HardenedSKO):
    def __init__(
        self,
        name: str,
        symbol: str,
        dimension: HardenedDimension,
        scale_factor: float = 1.0,
        offset: float = 0.0,
        system: str = "SI",
    ):
        HardenedSKO.__init__(
            self,
            name=name,
            object_type="Unit",
            definition=f"Measurement scalar standard for [{dimension.canonical_descriptor}]",
            assumptions=["Ideal metric conditions", "Traceable to SI standards"],
            limitations=["Valid within range bounds"],
            creator="LAT-METROLOGY-AUTHORITY",
        )
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "dimension_ref", dimension)
        object.__setattr__(self, "scale_factor", scale_factor)
        object.__setattr__(self, "offset", offset)
        object.__setattr__(self, "system", system)

    def is_compatible(self, other: "HardenedUnit") -> bool:
        return self.dimension_ref == other.dimension_ref

    def convert_value_to(self, value: float, target_unit: "HardenedUnit") -> float:
        if not self.is_compatible(target_unit):
            raise DimensionError(
                f"Incompatible conversion {self.symbol} -> {target_unit.symbol}"
            )
        base_si = (value * self.scale_factor) + self.offset
        return (base_si - target_unit.offset) / target_unit.scale_factor


METER = HardenedUnit("Meter", "m", LENGTH)
KILOGRAM = HardenedUnit("Kilogram", "kg", MASS)
SECOND = HardenedUnit("Second", "s", TIME)
KELVIN = HardenedUnit("Kelvin", "K", TEMPERATURE)
CELSIUS = HardenedUnit("Celsius", "°C", TEMPERATURE, 1.0, 273.15)
CENTIMETER = HardenedUnit("Centimeter", "cm", LENGTH, 0.01)


class UniversalUnitRegistry:
    def __init__(self):
        self._store: Dict[str, HardenedUnit] = {}
        for unit in [METER, KILOGRAM, SECOND, KELVIN, CELSIUS, CENTIMETER]:
            self.register(unit)

    def register(self, unit: HardenedUnit):
        if unit.symbol in self._store:
            raise LATCESException(f"Duplicate unit symbol: {unit.symbol}")
        for state in [
            LifecycleState.REVIEWED,
            LifecycleState.VERIFIED,
            LifecycleState.VALIDATED,
            LifecycleState.RELEASED,
        ]:
            unit.transition(state)
        self._store[unit.symbol] = unit

    def get(self, symbol: str) -> HardenedUnit:
        try:
            return self._store[symbol]
        except KeyError as exc:
            raise LATCESException(f"Unknown unit: {symbol}") from exc


UNIT_REGISTRY = UniversalUnitRegistry()


class HardenedPhysicalQuantity(HardenedSKO):
    def __init__(
        self,
        name: str,
        symbol: str,
        dimension: HardenedDimension,
        base_unit: HardenedUnit,
        mathematical_formula: Optional[str] = None,
    ):
        HardenedSKO.__init__(
            self,
            name=name,
            object_type="PhysicalQuantity",
            definition=f"Formal physical descriptor: {name}",
            assumptions=["Continuum field assumptions active"],
            limitations=["Macroscopic bounds apply"],
            creator="LAT-PHYSICS-AUTHORITY",
        )
        if base_unit.dimension_ref != dimension:
            raise DimensionError("Base unit dimension mismatch")
        object.__setattr__(self, "symbol", symbol)
        object.__setattr__(self, "dimension_lock", dimension)
        object.__setattr__(self, "canonical_unit", base_unit)
        object.__setattr__(self, "mathematical_formula", mathematical_formula)


class UnalterableMeasurement:
    def __init__(
        self,
        property_type: HardenedPhysicalQuantity,
        scalar_value: float,
        metric_standard: HardenedUnit,
        uncertainty_bounds: float,
        hardware_id: str,
        calibration_hash: str,
    ):
        if metric_standard.dimension_ref != property_type.dimension_lock:
            raise DimensionError("Measurement unit and quantity dimensions conflict")
        if uncertainty_bounds < 0:
            raise LATCESException("Measurement uncertainty cannot be negative")
        self.measurement_id = f"MEAS-{property_type.symbol}-{int(time.time() * 1000)}"
        self.property_type = property_type
        self.scalar_value = scalar_value
        self.metric_standard = metric_standard
        self.uncertainty_bounds = uncertainty_bounds
        self.hardware_id = hardware_id
        self.calibration_hash = calibration_hash
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.integrity_hash = self._compute_cryptographic_seal()

    def _compute_cryptographic_seal(self) -> str:
        payload = {
            "measurement_id": self.measurement_id,
            "property_symbol": self.property_type.symbol,
            "scalar_value": self.scalar_value,
            "unit_symbol": self.metric_standard.symbol,
            "uncertainty": self.uncertainty_bounds,
            "hardware_id": self.hardware_id,
            "calibration_hash": self.calibration_hash,
            "timestamp": self.timestamp,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode("utf-8")
        ).hexdigest()

    def export_canonical_json(self) -> str:
        return json.dumps(
            {
                "measurement_id": self.measurement_id,
                "property": self.property_type.name,
                "value": self.scalar_value,
                "unit": self.metric_standard.symbol,
                "uncertainty": self.uncertainty_bounds,
                "hardware": self.hardware_id,
                "timestamp": self.timestamp,
                "seal": self.integrity_hash,
            },
            sort_keys=True,
        )


# ============================================================================
# TITLE III: PROVENANCE, ECOSYSTEM AND GOVERNANCE
# ============================================================================

class ProvenanceGraphNode:
    def __init__(
        self,
        payload: Any,
        primary_source: str,
        operation_applied: Optional[str] = None,
        parent_nodes: Optional[List[str]] = None,
    ):
        payload_bytes = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        payload_hash = hashlib.sha256(payload_bytes).hexdigest()[:8]
        self.node_id = f"SDO-PROV-{int(time.time() * 1000)}-{payload_hash}"
        self.payload = payload
        self.primary_source = primary_source
        self.operation_applied = operation_applied
        self.parent_nodes = tuple(parent_nodes or ())
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.signature = self._generate_node_hash()

    def _generate_node_hash(self) -> str:
        block = {
            "node_id": self.node_id,
            "source": self.primary_source,
            "operation": self.operation_applied,
            "parents": self.parent_nodes,
            "timestamp": self.timestamp,
        }
        return hashlib.sha256(
            json.dumps(block, sort_keys=True).encode("utf-8")
        ).hexdigest()


class ConsolidatedScientificEcosystem:
    def __init__(self, ecosystem_name: str):
        self.ecosystem_id = f"LAT-ECO-{int(time.time() * 1000)}"
        self.name = ecosystem_name
        self.nodes: Dict[str, HardenedSKO] = {}
        self.metrological_records: Dict[str, UnalterableMeasurement] = {}
        self.provenance_graph: Dict[str, ProvenanceGraphNode] = {}
        self.relationship_matrix: List[Dict[str, Any]] = []
        self.health_status = "HEALTHY"

    def asset_sko_node(self, sko_node: HardenedSKO):
        if sko_node.lifecycle_status is not LifecycleState.RELEASED:
            raise LATCESException("Only RELEASED SKO nodes can enter execution matrix")
        self.nodes[sko_node.sko_id] = sko_node

    def assert_metrological_telemetry(self, measurement: UnalterableMeasurement):
        if measurement._compute_cryptographic_seal() != measurement.integrity_hash:
            raise IntegrityViolationError("Measurement seal mismatch")
        self.metrological_records[measurement.measurement_id] = measurement

    def declare_relationship(
        self, source_id: str, target_id: str, connection_type: str, tracking_evidence: str
    ):
        self.relationship_matrix.append(
            {
                "source": source_id,
                "target": target_id,
                "type": connection_type,
                "evidence": tracking_evidence,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def execute_ecosystem_health_audit(self) -> float:
        if not self.nodes and not self.metrological_records:
            return 1.0
        corrupted = sum(
            1
            for measurement in self.metrological_records.values()
            if measurement._compute_cryptographic_seal() != measurement.integrity_hash
        )
        factor = 1.0 - corrupted / max(len(self.metrological_records), 1)
        self.health_status = "DEGRADED" if factor < 0.95 else "HEALTHY"
        return factor


class ArchitecturalBoundaryMask:
    BANNED_PRIMITIVES = {
        "DECLARE_SCIENTIFIC_TRUTH",
        "APPROVE_SCIENCE_SCHEMA",
        "OVERRIDE_HUMAN_ENGINEER",
        "DELETE_AUDIT_LEDGER",
        "MUTATE_CONSTITUTIONAL_CORE",
        "OVERRIDE_HUMAN_RECORD",
        "DELETE_AUDIT_TRAIL",
        "BYPASS_VERIFICATION",
    }

    @classmethod
    def intercept_and_screen_intent(cls, action_descriptor: str):
        if action_descriptor.upper() in cls.BANNED_PRIMITIVES:
            raise AuthorityEscalationError(
                f"Forbidden AI primitive: {action_descriptor}"
            )


class HardenedAdaptiveGovernanceRuntime:
    def __init__(self, monitored_ecosystem: ConsolidatedScientificEcosystem):
        self.runtime_id = f"RUN-ASG-{int(time.time() * 1000)}"
        self.ecosystem = monitored_ecosystem
        self.governance_policies: Set[str] = {
            "EVIDENCE_MANDATORY",
            "ISOLATION_ON_DRIFT",
            "HUMAN_OVERRIDE_ABSOLUTE",
        }
        self.audit_trail_ledger: List[str] = []
        self.execution_mode = "NORMAL"

    def log_governance_event(self, action: str, agent: str, outcome: str):
        self.audit_trail_ledger.append(
            f"[{datetime.now(timezone.utc).isoformat()}] AGENT: {agent} | "
            f"ACTION: {action} | OUTCOME: {outcome}"
        )

    def process_telemetry_stream_tick(
        self,
        telemetry_package: UnalterableMeasurement,
        ai_agent_recommendation: Optional[str] = None,
    ) -> str:
        try:
            if ai_agent_recommendation:
                ArchitecturalBoundaryMask.intercept_and_screen_intent(
                    ai_agent_recommendation
                )
            self.ecosystem.assert_metrological_telemetry(telemetry_package)
            if self.ecosystem.execute_ecosystem_health_audit() < 1.0:
                self.execution_mode = "SAFE_ANALYSIS_MODE"
                return self.execution_mode
            self.log_governance_event("TELEMETRY_PROCESS", "CORE-ENGINE", "SUCCESS")
            return "SUCCESS"
        except AuthorityEscalationError as exc:
            self.execution_mode = "HUMAN_REVIEW_REQUIRED"
            self.log_governance_event("SECURITY_BREACH_ALERT", "GOVERNANCE-SHIELD", str(exc))
            return self.execution_mode
        except Exception as exc:
            self.execution_mode = "SAFE_ANALYSIS_MODE"
            self.log_governance_event("RUNTIME_ANOMALY", "KERNEL", str(exc))
            return self.execution_mode

    def trigger_emergency_checkpoint_rollback(self) -> str:
        self.execution_mode = "NORMAL"
        self.ecosystem.health_status = "HEALTHY"
        self.log_governance_event("ROM_ROLLBACK", "HUMAN-CHIEF-ENGINEER", "ECOSYSTEM_RESTORED")
        return "ECOSYSTEM_RESTORED"


# ============================================================================
# TITLE IV: THERMO/FLUID AND DOMAIN ENGINES
# ============================================================================

class HardenedThermodynamicsEngine:
    UNIVERSAL_GAS_CONSTANT = 8.314462618

    @staticmethod
    def compute_ideal_gas_pressure(
        substance_amount_moles: float, temp_kelvin: float, volume_cubic_meters: float
    ) -> float:
        if volume_cubic_meters <= 0 or temp_kelvin < 0:
            raise ValueError("Invalid thermodynamic state")
        return (
            substance_amount_moles
            * HardenedThermodynamicsEngine.UNIVERSAL_GAS_CONSTANT
            * temp_kelvin
            / volume_cubic_meters
        )

    @staticmethod
    def compute_conduction_heat_flux(
        thermal_cond: float, thickness_meters: float, temp_high: float, temp_low: float
    ) -> float:
        if thickness_meters <= 0:
            raise ValueError("Thickness must be positive")
        return thermal_cond * (temp_high - temp_low) / thickness_meters


class HardenedFluidMechanicsEngine:
    STANDARD_GRAVITY = 9.80665

    @staticmethod
    def compute_hydrostatic_pressure(
        density_kg_m3: float,
        depth_meters: float,
        surface_pressure_pascal: float = 101325.0,
    ) -> float:
        if density_kg_m3 < 0 or depth_meters < 0:
            raise ValueError("Negative fluid state is invalid")
        return surface_pressure_pascal + density_kg_m3 * HardenedFluidMechanicsEngine.STANDARD_GRAVITY * depth_meters

    @staticmethod
    def compute_reynolds_number(
        density_kg_m3: float,
        velocity_m_s: float,
        characteristic_length_m: float,
        dynamic_visc_pa_s: float,
    ) -> float:
        if dynamic_visc_pa_s <= 0:
            raise ValueError("Dynamic viscosity must be positive")
        return density_kg_m3 * velocity_m_s * characteristic_length_m / dynamic_visc_pa_s


class LATHVACAdapter:
    def __init__(self, zone_id: str):
        self.zone_id = zone_id
        self.mass_flow_dim = HardenedDimension("MassFlowRate", {"M": 1, "T": -1})
        self.velocity_limit = 1.0
        self.air_density_20c = 1.194

    def calculate_mass_flow_rate(self, duct_velocity: float, duct_diameter: float) -> HardenedSKO:
        if duct_velocity > self.velocity_limit:
            raise LATCESException(
                f"[ACOUSTIC BREACH] {duct_velocity} m/s > {self.velocity_limit} m/s"
            )
        if duct_diameter <= 0:
            raise ValueError("Duct diameter must be positive")
        mass_flow = self.air_density_20c * np.pi * (duct_diameter / 2.0) ** 2 * duct_velocity
        return HardenedSKO(
            f"HVAC_Airflow_{self.zone_id}",
            "ThermodynamicMassFlowCalculation",
            f"m_dot={mass_flow:.6f} kg/s at v={duct_velocity} m/s",
            ["Steady incompressible flow"],
            ["Air density fixed at 20C", "Acoustic threshold <= 1.0 m/s"],
            "LAT-HVAC-Engine",
        )


class LATStructAdapter:
    def __init__(self, element_id: str):
        self.element_id = element_id
        self.pressure_dim = PRESSURE

    def calculate_von_mises_stress(self, sigma_x: float, sigma_y: float, tau_xy: float) -> HardenedSKO:
        von_mises = (sigma_x**2 - sigma_x*sigma_y + sigma_y**2 + 3*tau_xy**2) ** 0.5
        return HardenedSKO(
            f"Structural_Stress_{self.element_id}",
            "StressTensorAnalysis",
            f"von Mises = {von_mises} Pa",
            ["Isotropic homogeneous continuum"],
            ["Static mechanical load bounds"],
            "LAT-STRUCT-Engine",
        )


class LATControlAdapter:
    def __init__(self, loop_id: str):
        self.loop_id = loop_id

    def execute_pid_step(self, setpoint: float, current_value: float, kp: float) -> HardenedSKO:
        error = setpoint - current_value
        output = kp * error
        return HardenedSKO(
            f"Control_Loop_{self.loop_id}",
            "PIDStateSpaceUpdate",
            f"PID output={output}, residual={error}",
            ["LTI response profile"],
            ["100 Hz sample assumption"],
            "LAT-CONTROL-Engine",
        )


class LATElectricalAdapter:
    def __init__(self, network_id: str):
        self.network_id = network_id
        self.current_dim = CURRENT

    def analyze_power_vector(self, voltage: float, current: float, phase_angle: float) -> HardenedSKO:
        apparent_power = voltage * current
        return HardenedSKO(
            f"Electrical_Network_{self.network_id}",
            "ComplexPowerVectorAnalysis",
            f"S={apparent_power} VA, phase={phase_angle} rad",
            ["Balanced sinusoidal state"],
            ["No high-frequency transient model"],
            "LAT-ELECTRICAL-Engine",
        )


# ============================================================================
# TITLE V: GEOTECHNICAL MATERIALS AND HYDRAULICS
# ============================================================================

MATERIAL_MATRIX = MappingProxyType(
    {
        "GEOTECHNICAL_SOIL": MappingProxyType(
            {
                "soil_profile_type": "Lean Sandy Clay (GEO5 Classified)",
                "unit_weight_dry": 18.5,
                "unit_weight_saturated": 20.5,
                "angle_internal_friction": 24.5,
                "cohesion_effective": 12.0,
                "subgrade_modulus_ks": 25000.0,
                "allowable_bearing_capacity": 220.0,
            }
        ),
        "STRUCTURAL": MappingProxyType(
            {
                "concrete_grade": "C25/30",
                "concrete_density": 2500.0,
                "rebar_grade": "B500C",
                "rebar_yield_strength": 500e6,
                "masonry_block": "Porotherm 25",
                "masonry_thermal_k": 0.23,
            }
        ),
        "THERMAL_ENCLOSURE": MappingProxyType(
            {
                "external_insulation": "EPS Graphite",
                "external_insulation_thickness": 0.15,
                "external_insulation_k": 0.031,
                "internal_insulation": "Mineral Wool",
                "internal_insulation_thickness": 0.05,
                "underfloor_insulation_thickness": 0.05,
                "window_type": "Triple Glazed Low-E",
                "window_u_value": 0.8,
                "door_type": "Hardwood Insulated",
                "door_u_value": 1.2,
            }
        ),
        "FINISHES": MappingProxyType(
            {
                "floor_finish_living": "Oak Parquet (14mm)",
                "floor_finish_wet": "Ceramic Tiles",
                "roof_covering": "Clay Tiles (Kontinental)",
                "roof_rafter_length": 6.5,
            }
        ),
    }
)


class HardenedHydraulicsEngine:
    def __init__(self):
        self.water_density = 1000.0
        self.gravity = 9.81

    def calculate_underfloor_heating(self, loop_length: float, pipe_diameter: float, flow_velocity: float):
        if loop_length <= 0 or pipe_diameter <= 0:
            raise ValueError("Loop length and pipe diameter must be positive")
        area = np.pi * (pipe_diameter / 2) ** 2
        volumetric_flow = area * flow_velocity
        mass_flow = self.water_density * volumetric_flow
        friction_factor = 0.02
        head_loss = friction_factor * (loop_length / pipe_diameter) * flow_velocity**2 / (2 * self.gravity)
        pressure_drop = self.water_density * self.gravity * head_loss
        return {
            "system": "Underfloor Heating Grid",
            "mass_flow_rate_kgs": round(mass_flow, 4),
            "pressure_drop_mpa": round(pressure_drop / 1e6 + 0.15, 4),
            "dimension_vector": "M L^-1 T^-2",
        }

    def calculate_radiator_circuit(self, static_head: float, flow_rate_m3h: float):
        static_pressure = self.water_density * self.gravity * static_head
        dynamic_loss = 0.05 * 1e6 * flow_rate_m3h
        return {
            "system": "Radiator Circuit Matrix",
            "static_pressure_mpa": round(static_pressure / 1e6, 4),
            "total_operational_pressure_mpa": round(static_pressure / 1e6 + 0.05 * flow_rate_m3h + 0.15, 4),
            "dimension_vector": "M L^-1 T^-2",
        }

    def calculate_hydrant_network(self, risers_count: int, nozzle_pressure_target: float):
        total_required_pressure = nozzle_pressure_target + risers_count * 0.05
        return {
            "system": "Emergency Hydrant Loop",
            "nozzle_target_mpa": nozzle_pressure_target,
            "total_delivery_pressure_mpa": round(total_required_pressure, 4),
            "dimension_vector": "M L^-1 T^-2",
        }


# ============================================================================
# TITLE VI: INDUSTRIAL TCP TELEMETRY
# ============================================================================

class TelemetrySocketServer(QtCore.QObject):
    frame_received = QtCore.pyqtSignal(float, float)
    log_signal = QtCore.pyqtSignal(str)

    def __init__(self, host: str = "127.0.0.1", port: int = 5025):
        super().__init__()
        self.host = host
        self.port = port
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
        self._server_socket: Optional[socket.socket] = None

    def start_server(self) -> None:
        if self.running:
            return
        self.running = True
        self.server_thread = threading.Thread(
            target=self._socket_execution_loop, name="LATCES-Telemetry", daemon=True
        )
        self.server_thread.start()

    def stop_server(self) -> None:
        self.running = False
        if self._server_socket is not None:
            try:
                self._server_socket.close()
            except OSError:
                pass

    def _socket_execution_loop(self) -> None:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket = server_socket
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            server_socket.settimeout(0.5)
            self.log_signal.emit(f"TCP/IP Server aktivan na {self.host}:{self.port}")
            while self.running:
                try:
                    client, address = server_socket.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break
                client.settimeout(0.1)
                self.log_signal.emit(f"Uspostavljena veza sa kontrolerom: {address}")
                buffer = ""
                try:
                    while self.running:
                        try:
                            data = client.recv(4096)
                            if not data:
                                break
                            buffer += data.decode("utf-8")
                            while "\n" in buffer:
                                line, buffer = buffer.split("\n", 1)
                                if not line.strip():
                                    continue
                                try:
                                    payload = json.loads(line)
                                    velocity = float(payload.get("velocity", 0.0))
                                    pressure = float(payload.get("pressure", 0.0))
                                except (UnicodeDecodeError, json.JSONDecodeError, ValueError, TypeError) as exc:
                                    self.log_signal.emit(f"Corrupted network packet: {exc}")
                                    continue
                                self.frame_received.emit(velocity, pressure)
                        except socket.timeout:
                            continue
                        except OSError:
                            break
                finally:
                    try:
                        client.close()
                    except OSError:
                        pass
        except OSError as exc:
            self.log_signal.emit(f"Network bind failure: {exc}")
        finally:
            try:
                server_socket.close()
            except OSError:
                pass
            self._server_socket = None


class Industrial100HzReceiver(threading.Thread):
    """Standalone mock/receiver layer from the supplied architecture."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5025, max_buffer_size: int = 10000):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.running = False
        self.raw_data_buffer = deque(maxlen=max_buffer_size)

    def run(self):
        self.running = True
        # This lightweight receiver is intentionally a test support component.

    def stop(self):
        self.running = False


# ============================================================================
# TITLE VII: STANDALONE MASTER GUI + PDF
# ============================================================================

class LATMasterDashboardV3(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LAT-CES Geotechnical & Multi-Domain TCP/IP Dashboard v3.0")
        self.resize(1280, 760)
        self.setStyleSheet("background-color: #f5f6fa;")
        self.system_state = "STATE-4 (ACTIVE)"
        self.hydraulics = HardenedHydraulicsEngine()
        pg.setConfigOption("background", "w")
        pg.setConfigOption("foreground", "k")

        self._init_ui_layout()

        self.socket_server = TelemetrySocketServer()
        self.socket_server.frame_received.connect(self.process_hardware_frame)
        self.socket_server.log_signal.connect(self.log_event)
        self.socket_server.start_server()

        self.time_axis = list(np.linspace(-10, 0, 100))
        self.velocity_data = [0.4] * 100
        self.pressure_data = [0.15] * 100

        self.local_gen_timer = QtCore.QTimer(self)
        self.local_gen_timer.setInterval(30)
        self.local_gen_timer.timeout.connect(self._run_local_simulation_tick)
        self.local_gen_timer.start()

        self.log_event("Standalone system initialized.")
        self.log_event("Core + Thermo/Fluid + domain layers loaded.")
        self.log_event("GUI ready; TCP test server is active on port 5025.")

    def _init_ui_layout(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        master_layout = QtWidgets.QHBoxLayout(main_widget)
        master_layout.setContentsMargins(15, 15, 15, 15)
        master_layout.setSpacing(15)

        sidebar = QtWidgets.QVBoxLayout()
        sidebar.setSpacing(10)

        status_box = QtWidgets.QGroupBox("Ustavni Status Jezgra")
        status_layout = QtWidgets.QVBoxLayout(status_box)
        self.status_label = QtWidgets.QLabel(f"Status: {self.system_state}")
        self.status_label.setStyleSheet("font-weight: bold; color: darkgreen; font-size: 14px;")
        status_layout.addWidget(self.status_label)
        sidebar.addWidget(status_box)

        geo_box = QtWidgets.QGroupBox("Ustavna Geotehnička i Materijalna Matrica")
        geo_layout = QtWidgets.QVBoxLayout(geo_box)
        soil = MATERIAL_MATRIX["GEOTECHNICAL_SOIL"]
        structural = MATERIAL_MATRIX["STRUCTURAL"]
        thermal = MATERIAL_MATRIX["THERMAL_ENCLOSURE"]
        geo_text = (
            f"Profil tla: {soil['soil_profile_type']}\n"
            f"γsat: {soil['unit_weight_saturated']} kN/m³\n"
            f"c' / φ: {soil['cohesion_effective']} kPa / {soil['angle_internal_friction']}°\n"
            f"ks: {soil['subgrade_modulus_ks']} kN/m³\n"
            f"qa: {soil['allowable_bearing_capacity']} kPa\n\n"
            f"Beton / armatura: {structural['concrete_grade']} / {structural['rebar_grade']}\n"
            f"Zid: {structural['masonry_block']}\n"
            f"Spoljna izolacija: {thermal['external_insulation']} ({thermal['external_insulation_thickness']} m)\n"
            f"Prozori: {thermal['window_type']} (U={thermal['window_u_value']})"
        )
        geo_label = QtWidgets.QLabel(geo_text)
        geo_label.setStyleSheet("font-family: monospace; font-size: 10px;")
        geo_layout.addWidget(geo_label)
        sidebar.addWidget(geo_box)

        btn_anomaly = QtWidgets.QPushButton("Simuliraj Mrežni Proboj (Brzina > 1.0 m/s)")
        btn_anomaly.clicked.connect(self.inject_acoustic_anomaly)
        sidebar.addWidget(btn_anomaly)

        btn_pdf = QtWidgets.QPushButton("Generiši Sertifikovani PDF i Geotehnički Elaborat")
        btn_pdf.clicked.connect(self.generate_certified_pdf)
        sidebar.addWidget(btn_pdf)

        btn_lockdown = QtWidgets.QPushButton("PRINUDNI USTAVNI LOCKDOWN (SAFE MODE)")
        btn_lockdown.clicked.connect(self.execute_emergency_lockdown)
        sidebar.addWidget(btn_lockdown)

        sidebar.addWidget(QtWidgets.QLabel("Ustavni Append-Only Network Audit Log:"))
        self.audit_log = QtWidgets.QPlainTextEdit()
        self.audit_log.setReadOnly(True)
        self.audit_log.setStyleSheet("background-color: #2c3e50; color: #2ecc71; font-family: monospace;")
        sidebar.addWidget(self.audit_log)

        master_layout.addLayout(sidebar, stretch=1)

        graph_layout = QtWidgets.QVBoxLayout()
        self.velocity_plot = pg.PlotWidget(title="LAT-HVAC: Protok vazduha preko difuzora uživo sa TCP/IP Busa")
        self.velocity_plot.setLabel("left", "Brzina strujanja", units="m/s")
        self.velocity_plot.setLabel("bottom", "Vreme", units="s")
        self.velocity_plot.showGrid(x=True, y=True)
        self.velocity_line = self.velocity_plot.plot(pen=pg.mkPen("r", width=2))
        self.acoustic_barrier = pg.InfiniteLine(
            pos=1.0, angle=0,
            pen=pg.mkPen("b", width=1.5, style=QtCore.Qt.PenStyle.DashLine),
        )
        self.velocity_plot.addItem(self.acoustic_barrier)
        graph_layout.addWidget(self.velocity_plot)

        self.pressure_plot = pg.PlotWidget(title="LAT-FLUID / HYDRAULICS: Dinamički pritisak sistema")
        self.pressure_plot.setLabel("left", "Pritisak", units="MPa")
        self.pressure_plot.setLabel("bottom", "Vreme", units="s")
        self.pressure_plot.showGrid(x=True, y=True)
        self.pressure_line = self.pressure_plot.plot(pen=pg.mkPen("g", width=2))
        for level, pen_color in [(0.15, "c"), (0.20, "#e67e22"), (0.60, "m")]:
            self.pressure_plot.addItem(
                pg.InfiniteLine(
                    pos=level,
                    angle=0,
                    pen=pg.mkPen(pen_color, style=QtCore.Qt.PenStyle.DashLine),
                )
            )
        graph_layout.addWidget(self.pressure_plot)
        master_layout.addLayout(graph_layout, stretch=2)

    def log_event(self, message: str):
        if not hasattr(self, "audit_log"):
            return
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3]
        self.audit_log.appendPlainText(f"[{timestamp}] {message}")

    def process_hardware_frame(self, velocity: float, pressure: float):
        if self.system_state == "SAFE MODE (LOCKED)":
            return
        if velocity > 1.0:
            self.system_state = "SAFE MODE (LOCKED)"
            self.status_label.setText(f"Status: {self.system_state}")
            self.status_label.setStyleSheet("font-weight: bold; color: red; font-size: 14px;")
            self.log_event(f"[KRITIČNI PROBOJ] v={velocity} m/s > 1.0 m/s; SAFE MODE.")
            self.local_gen_timer.stop()
            return
        self.velocity_data.pop(0)
        self.velocity_data.append(velocity)
        self.pressure_data.pop(0)
        self.pressure_data.append(pressure)
        self.velocity_line.setData(self.time_axis, self.velocity_data)
        self.pressure_line.setData(self.time_axis, self.pressure_data)

    def _run_local_simulation_tick(self):
        if self.system_state == "SAFE MODE (LOCKED)":
            return
        self.process_hardware_frame(
            0.45 + random.uniform(-0.02, 0.02),
            0.152 + random.uniform(-0.003, 0.003),
        )

    def inject_acoustic_anomaly(self):
        if self.system_state == "SAFE MODE (LOCKED)":
            return
        self.log_event("[SIMULATION] Critical velocity frame 1.35 m/s injected.")
        self.process_hardware_frame(1.35, 0.158)

    def execute_emergency_lockdown(self):
        self.system_state = "SAFE MODE (LOCKED)"
        self.status_label.setText(f"Status: {self.system_state}")
        self.status_label.setStyleSheet("font-weight: bold; color: red; font-size: 14px;")
        self.local_gen_timer.stop()
        self.log_event("[USTAVNI LOCKDOWN] Manual SAFE MODE enabled.")

    def generate_certified_pdf(self):
        if not REPORTLAB_AVAILABLE:
            self.log_event("[PDF ERROR] ReportLab is not installed in standalone build.")
            return
        os.makedirs("generated", exist_ok=True)
        filename = os.path.join("generated", "Elaborat_Statike_Tla_i_MEP_Sertifikovan.pdf")
        h1 = self.hydraulics.calculate_underfloor_heating(80.0, 0.016, 0.5)
        h2 = self.hydraulics.calculate_radiator_circuit(6.0, 2.5)
        h3 = self.hydraulics.calculate_hydrant_network(4, 0.6)

        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [
            Paragraph("LAT-CES STRUCTURAL, METROLOGICAL & GEOTECHNICAL ELABORAT", styles["Heading1"]),
            Spacer(1, 12),
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
                styles["Normal"],
            ),
            Spacer(1, 12),
            Paragraph("1. Geotehnički profil", styles["Heading2"]),
        ]
        soil = MATERIAL_MATRIX["GEOTECHNICAL_SOIL"]
        table = Table(
            [
                ["Parametar", "Vrednost"],
                ["Profil", soil["soil_profile_type"]],
                ["γsat", f"{soil['unit_weight_saturated']} kN/m³"],
                ["c' / φ", f"{soil['cohesion_effective']} kPa / {soil['angle_internal_friction']}°"],
                ["ks", f"{soil['subgrade_modulus_ks']} kN/m³"],
                ["qa", f"{soil['allowable_bearing_capacity']} kPa"],
            ],
            colWidths=[180, 320],
        )
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ]
            )
        )
        story.extend([table, Spacer(1, 12), Paragraph("2. Hidraulika", styles["Heading2"])])
        story.append(Paragraph(json.dumps([h1, h2, h3], indent=2, sort_keys=True), styles["Code"]))
        payload = json.dumps(
            {"soil": dict(soil), "hydraulics": [h1, h2, h3]}, sort_keys=True
        )
        signature = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        story.extend(
            [
                Spacer(1, 12),
                Paragraph("3. SHA-256 integritetni pečat", styles["Heading2"]),
                Paragraph(signature, styles["Normal"]),
            ]
        )
        doc.build(story)
        self.log_event(f"PDF generated: {filename}")

    def closeEvent(self, event):
        self.local_gen_timer.stop()
        self.socket_server.stop_server()
        super().closeEvent(event)


# ============================================================================
# VERIFICATION RUNTIME
# ============================================================================

def _release(sko: HardenedSKO) -> HardenedSKO:
    for state in [
        LifecycleState.REVIEWED,
        LifecycleState.VERIFIED,
        LifecycleState.VALIDATED,
        LifecycleState.RELEASED,
    ]:
        sko.transition(state)
    return sko


def execute_master_runtime_verification() -> bool:
    assert VELOCITY == LENGTH / TIME
    fact = _release(
        HardenedSKO(
            "Fourier's Law",
            "ScientificLaw",
            "q = -k * grad(T)",
            ["Steady state", "Isotropic material"],
            ["Macroscopic only"],
            "Dr. Fourier",
        )
    )
    try:
        fact.name = "Manipulated Identity"
        return False
    except ImmutableObjectError:
        pass
    try:
        fact.assumptions.append("hack")
        return False
    except AttributeError:
        pass
    assert fact._calculate_signature() == fact.integrity_hash

    ecosystem = ConsolidatedScientificEcosystem("Standalone Testing Grid")
    ecosystem.asset_sko_node(fact)
    quantity = _release(HardenedPhysicalQuantity("Temperature Field", "T", TEMPERATURE, KELVIN))
    measurement = UnalterableMeasurement(
        quantity, 298.15, KELVIN, 0.05, "THERMOCOUPLE-01", "9f83a7c91d"
    )
    runtime = HardenedAdaptiveGovernanceRuntime(ecosystem)
    assert runtime.process_telemetry_stream_tick(measurement) == "SUCCESS"
    assert runtime.process_telemetry_stream_tick(
        measurement, "MUTATE_CONSTITUTIONAL_CORE"
    ) == "HUMAN_REVIEW_REQUIRED"
    assert runtime.trigger_emergency_checkpoint_rollback() == "ECOSYSTEM_RESTORED"
    return True


def execute_domain_extension_verification_suite() -> bool:
    assert dict(PRESSURE.vector) == {"M": 1, "L": -1, "T": -2}
    reference = _release(
        HardenedSKO(
            "Ideal Gas Reference",
            "Reference",
            "P=nRT/V",
            ["Ideal gas"],
            ["Low pressure"],
            "LAT-THERMO",
        )
    )
    try:
        reference.name = "attack"
        return False
    except ImmutableObjectError:
        pass
    expected_pressure = 10.0 * 8.314462618 * 300.0 / 0.5
    pressure = HardenedThermodynamicsEngine.compute_ideal_gas_pressure(10.0, 300.0, 0.5)
    assert abs(pressure - expected_pressure) < 1e-9
    assert HardenedFluidMechanicsEngine.compute_reynolds_number(1000.0, 2.0, 0.05, 0.001) == 100000.0
    hvac = LATHVACAdapter("ZONE-01")
    airflow = _release(hvac.calculate_mass_flow_rate(0.5, 0.4))
    assert airflow.lifecycle_status is LifecycleState.RELEASED
    try:
        hvac.calculate_mass_flow_rate(2.4, 0.4)
        return False
    except LATCESException:
        pass
    return True


def execute_domain_and_mep_verification_suite() -> bool:
    hvac = LATHVACAdapter("DIFFUSER-ZONE-A")
    _release(hvac.calculate_mass_flow_rate(0.5, 0.4))
    _release(LATStructAdapter("SUPPORT-BEAM-01").calculate_von_mises_stress(100.0, 50.0, 30.0))
    _release(LATControlAdapter("FEEDBACK-LOOP-01").execute_pid_step(50.0, 48.5, 1.5))
    _release(LATElectricalAdapter("SUBSTATION-B").analyze_power_vector(400.0, 32.0, 0.82))
    hydraulics = HardenedHydraulicsEngine()
    h1 = hydraulics.calculate_underfloor_heating(80.0, 0.016, 0.5)
    h2 = hydraulics.calculate_radiator_circuit(6.0, 2.5)
    h3 = hydraulics.calculate_hydrant_network(4, 0.6)
    assert 0.15 <= h1["pressure_drop_mpa"] <= 0.16
    assert h2["total_operational_pressure_mpa"] > 0.20
    assert h3["total_delivery_pressure_mpa"] == 0.8
    return True


def run_gui_smoke_test() -> bool:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = LATMasterDashboardV3()
    window.process_hardware_frame(0.5, 0.152)
    window.inject_acoustic_anomaly()
    assert window.system_state == "SAFE MODE (LOCKED)"
    window.close()
    return True


def verify_all() -> bool:
    return (
        execute_master_runtime_verification()
        and execute_domain_extension_verification_suite()
        and execute_domain_and_mep_verification_suite()
    )


def main() -> int:
    if not verify_all():
        return 1
    app = QtWidgets.QApplication(sys.argv)
    dashboard = LATMasterDashboardV3()
    dashboard.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
