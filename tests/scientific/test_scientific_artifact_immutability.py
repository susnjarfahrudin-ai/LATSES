from __future__ import annotations

import pytest

from lat_ces.scientific.core.building_adapter import to_building_result
from lat_ces.scientific.core.governance import (
    ArtifactRegistry,
    LifecycleEngine,
    LifecycleState,
    ScientificArtifact,
)


def _validated_artifact() -> ScientificArtifact:
    artifact = ScientificArtifact(
        artifact_id="ARTIFACT-IMMUTABILITY-001",
        sci_id="LAT-SCI-CORE-0145",
        kind="engineering-result",
        version=1,
        state=LifecycleState.DRAFT,
        content={"geometry": {"height_m": 3.0, "layers": ["wall", "insulation"]}},
        provenance=("test:source",),
    ).with_hash()
    artifact = LifecycleEngine().transition(artifact, LifecycleState.VALIDATED)
    return artifact


def test_scientific_artifact_freezes_nested_content_and_hash():
    source = {"geometry": {"height_m": 3.0, "layers": ["wall"]}}
    artifact = ScientificArtifact(
        artifact_id="ARTIFACT-IMMUTABILITY-002",
        sci_id="LAT-SCI-CORE-0145",
        kind="engineering-result",
        version=1,
        state=LifecycleState.DRAFT,
        content=source,
        provenance=("test:source",),
    ).with_hash()
    original_hash = artifact.content_hash

    source["geometry"]["height_m"] = 9.0
    source["geometry"]["layers"].append("roof")

    assert artifact.content["geometry"]["height_m"] == 3.0
    assert artifact.content["geometry"]["layers"] == ("wall",)
    assert artifact.content_hash == original_hash

    with pytest.raises(TypeError):
        artifact.content["geometry"]["height_m"] = 4.0
    with pytest.raises(AttributeError):
        artifact.content["geometry"]["layers"].append("roof")


def test_registry_and_building_boundary_accept_only_intact_validated_artifact():
    artifact = _validated_artifact().with_hash()
    registered = ArtifactRegistry().register(artifact)
    result = to_building_result(registered)

    assert result.artifact_id == artifact.artifact_id
    assert result.sci_id == "LAT-SCI-CORE-0145"
    assert result.state == "VALIDATED"
    assert result.content["geometry"]["height_m"] == 3.0
    assert result.content_hash == artifact.content_hash
