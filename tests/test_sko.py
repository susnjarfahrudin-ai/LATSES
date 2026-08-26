import pytest

from lat_ces.core.sko import ScientificKnowledgeObject, SKOState


def test_sko_immutability():
    sko = ScientificKnowledgeObject("SKO-001", "Test SKO", {"param": 42})
    assert sko.state == SKOState.DRAFT

    sko_hash = sko.lock_and_release()
    assert sko.state == SKOState.RELEASED
    assert len(sko_hash) == 64
    assert sko.release_hash == sko_hash
    assert sko.released_at is not None

    with pytest.raises(AttributeError):
        sko.title = "Novi Naslov"


def test_sko_hash_is_deterministic():
    sko = ScientificKnowledgeObject("sko-002", "Deterministic", {"nested": {"b": 2}})

    first_hash = sko.compute_hash()
    second_hash = sko.compute_hash()

    assert first_hash == second_hash


def test_sko_portable_identity_and_predecessor_metadata():
    sko = ScientificKnowledgeObject(
        name="Heat Transfer Law",
        object_type="ScientificLaw",
        definition="Fourier conduction law",
        semantic_id="LAT-SKO-LAW-00000001",
        version="1.1",
        predecessor_id="LAT-SKO-LAW-00000000",
        provenance={"source": "reference-text"},
        verification_refs=["LAT-SKO-VERIFY-00000001"],
        validation_refs=["LAT-SKO-VALID-00000001"],
    )

    assert sko.semantic_id == "LAT-SKO-LAW-00000001"
    assert sko.version == "1.1"
    assert sko.predecessor_id == "LAT-SKO-LAW-00000000"
    assert sko.provenance == {"source": "reference-text"}
    assert sko.verification_refs == ["LAT-SKO-VERIFY-00000001"]
    assert sko.validation_refs == ["LAT-SKO-VALID-00000001"]
    assert sko.released_at is None


def test_sko_release_metadata_is_immutable_after_release():
    sko = ScientificKnowledgeObject(
        name="Measurement",
        object_type="Measurement",
        definition="Observed physical quantity",
    )
    sko.lock_and_release()

    with pytest.raises(AttributeError):
        sko.version = "2.0"

    with pytest.raises(AttributeError):
        sko.semantic_id = "LAT-SKO-MEAS-00000002"

    with pytest.raises(ValueError):
        sko.lock_and_release()
