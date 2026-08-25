"""Non-authoritative Reference House room preview geometry.

The current Reference House fixture declares room areas/heights/orientations but
not authoritative room coordinates or partition wall topology. This module
creates a deterministic visualization-only rectangle layout that preserves the
declared positive room areas inside the explicit 12 m x 10 m level envelope.

The result is explicitly DERIVED_PREVIEW and must not be passed to engineering
solvers or treated as the canonical BuildingModel geometry.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.reference_house import ReferenceHouse


@dataclass(frozen=True)
class PreviewRoomRectangle:
    level_id: str
    room_id: str
    name: str
    x_m: float
    y_m: float
    length_m: float
    width_m: float
    height_m: float
    status: str = "DERIVED_PREVIEW"
    engineering_usable: bool = False

    @property
    def area_m2(self) -> float:
        return self.length_m * self.width_m


@dataclass(frozen=True)
class PreviewLevelGeometry:
    level_id: str
    length_m: float
    width_m: float
    rooms: tuple[PreviewRoomRectangle, ...]
    status: str = "DERIVED_PREVIEW"


def _positive_rooms(level_data: dict) -> list[dict]:
    return [
        room
        for room in level_data["rooms"]
        if room.get("height_m", 0.0) > 0.0 and room.get("area_m2", 0.0) > 0.0
    ]


def derive_preview_geometry(reference_house: ReferenceHouse) -> tuple[PreviewLevelGeometry, ...]:
    """Create deterministic visualization rectangles without changing canonical geometry.

    The largest room is given a full-envelope-width leading band. Remaining
    positive-area rooms are packed side-by-side in a second band. This is a
    mathematical preview of the declared areas, not an architectural claim.
    """
    dimensions = reference_house.data["dimensions"]
    envelope_length = float(dimensions["length_m"])
    envelope_width = float(dimensions["width_m"])
    result: list[PreviewLevelGeometry] = []

    for level_data in reference_house.levels:
        rooms = sorted(_positive_rooms(level_data), key=lambda room: (-room["area_m2"], room["id"]))
        if not rooms:
            result.append(PreviewLevelGeometry(level_data["id"], envelope_length, envelope_width, ()))
            continue

        leading = rooms[0]
        leading_depth = float(leading["area_m2"]) / envelope_length
        remaining_area = sum(float(room["area_m2"]) for room in rooms[1:])
        remaining_depth = remaining_area / envelope_length if remaining_area else 0.0
        if leading_depth + remaining_depth > envelope_width + 1e-9:
            raise ValueError(f"Preview room areas do not fit level {level_data['id']}")

        previews: list[PreviewRoomRectangle] = [
            PreviewRoomRectangle(
                level_id=level_data["id"],
                room_id=leading["id"],
                name=leading["name"],
                x_m=0.0,
                y_m=0.0,
                length_m=envelope_length,
                width_m=leading_depth,
                height_m=float(leading["height_m"]),
            )
        ]

        cursor_x = 0.0
        for room in rooms[1:]:
            length_m = float(room["area_m2"]) / remaining_depth if remaining_depth else 0.0
            previews.append(
                PreviewRoomRectangle(
                    level_id=level_data["id"],
                    room_id=room["id"],
                    name=room["name"],
                    x_m=cursor_x,
                    y_m=leading_depth,
                    length_m=length_m,
                    width_m=remaining_depth,
                    height_m=float(room["height_m"]),
                )
            )
            cursor_x += length_m

        result.append(
            PreviewLevelGeometry(
                level_id=level_data["id"],
                length_m=envelope_length,
                width_m=envelope_width,
                rooms=tuple(previews),
            )
        )

    return tuple(result)


__all__ = ["PreviewRoomRectangle", "PreviewLevelGeometry", "derive_preview_geometry"]
