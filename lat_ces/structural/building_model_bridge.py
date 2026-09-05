"""Bridge structural solver results to the canonical BuildingModel.

The bridge is intentionally non-invasive: BuildingModel remains the canonical
owner of building state, while solver evidence is carried as an immutable
binding. No solver status is translated into the model's validation semantics.
In particular, ``VALID`` is not produced or modified by this layer.
"""
from __future__ import annotations

from dataclasses import dataclass

from lat_ces.building_model.core import BuildingModel
from lat_ces.structural.beam_solver import BeamSolverResult


@dataclass(frozen=True)
class StructuralSolverBinding:
    """Canonical-model identity paired with an independent solver result."""

    model: BuildingModel
    solver_result: BeamSolverResult

    @property
    def solver_converged(self) -> bool:
        return self.solver_result.status == "SOLVER_CONVERGED"


def bind_solver_result(
    model: BuildingModel,
    solver_result: BeamSolverResult,
) -> StructuralSolverBinding:
    """Bind solver evidence to the existing canonical model without mutation.

    The exact ``BuildingModel`` instance is retained. The solver result is
    preserved verbatim, including ``SOLVER_CONVERGED``/``SOLVER_FAILED``;
    this bridge deliberately does not create or infer a ``VALID`` state.
    """
    if not isinstance(model, BuildingModel):
        raise TypeError("model must be a BuildingModel")
    if not isinstance(solver_result, BeamSolverResult):
        raise TypeError("solver_result must be a BeamSolverResult")
    return StructuralSolverBinding(model=model, solver_result=solver_result)


__all__ = ["StructuralSolverBinding", "bind_solver_result"]
