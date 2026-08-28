"""Compatibility exports for the canonical production MEP model.

MEP ownership now lives in ``lat_ces.building.mep``. This module remains a
stable import path but does not define a second MEP domain model.
"""
from lat_ces.building.mep import HeatingZone, VentilationOpening, WaterBranch, group_by_room

__all__ = ["VentilationOpening", "WaterBranch", "HeatingZone", "group_by_room"]
