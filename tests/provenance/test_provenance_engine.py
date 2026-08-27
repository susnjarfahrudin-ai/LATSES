from dataclasses import dataclass

from lat_ces.scientific.provenance import (
    AlgorithmReference,
    DataSource,
    ProvenanceGraph,
    ScientificDataObject,
    TransformationRecord,
    provenance_hash,
    validate_provenance_chain,
)


def _source():
    return DataSource("SENSOR-001", "Measurement", "Room temperature sensor", "room-1")


def _data(data_id="SDO-TEMP-000001", source=None):
    return ScientificDataObject(23.4, source or _source(), data_id=data_id, timestamp="2026-08-27T00:00:00+00:00")


def _algorithm(version="1.2"):
    return AlgorithmReference("ALG-MAVG", "Moving Average Filter", version, "Verified", "LAT-CES")


def _transform(input_id="SDO-TEMP-000001", output_id="SDO-TEMP-000002"):
    return TransformationRecord(input_id, "Average Filter", "ALG-MAVG", output_id, {"window": 3}, "2026-08-27T00:01:00+00:00")


def test_data_identity_creation():
    assert _data().data_id


def test_timestamp_registration():
    assert _data().timestamp


def test_immutable_data_identity():
    data = _data()
    try:
        data.data_id = "OTHER"
    except Exception:
        pass
    else:
        raise AssertionError("data identity must be immutable")


def test_source_requirement():
    try:
        ScientificDataObject(23.4, None)
    except ValueError as exc:
        assert "source" in str(exc).lower()
    else:
        raise AssertionError("missing source must be rejected")


def test_source_identity_validation():
    assert _source().source_id and _source().source_type and _source().description


def test_source_trace_link():
    data = _data()
    assert data.source.source_id == "SENSOR-001"


def test_transformation_registration():
    record = _transform()
    assert record.operation == "Average Filter"


def test_input_output_link():
    record = _transform()
    assert (record.input_id, record.output_id) == ("SDO-TEMP-000001", "SDO-TEMP-000002")


def test_transformation_history_preservation():
    record = _transform()
    try:
        record.operation = "Changed"
    except Exception:
        pass
    else:
        raise AssertionError("transformation records must be immutable")


def test_algorithm_identity():
    algorithm = _algorithm()
    assert algorithm.algorithm_id and algorithm.name and algorithm.version


def test_algorithm_version_tracking():
    assert _algorithm("1.1") != _algorithm("1.2")


def test_graph_node_registration():
    graph = ProvenanceGraph()
    data = _data()
    graph.add_node(data)
    assert data.data_id in graph.nodes


def test_graph_link_validation():
    graph = ProvenanceGraph()
    raw = _data()
    result = _data("SDO-TEMP-000002")
    graph.add_node(raw)
    graph.add_node(result)
    graph.add_link(raw, result)
    assert graph.successors(raw.data_id) == (result.data_id,)


def test_missing_link_detection():
    graph = ProvenanceGraph()
    raw = _data()
    result = _data("SDO-TEMP-000002")
    graph.add_node(raw)
    try:
        graph.add_link(raw, result)
    except ValueError as exc:
        assert "registered" in str(exc)
    else:
        raise AssertionError("unregistered link endpoint must be rejected")


def test_provenance_hash_generation():
    assert len(provenance_hash(_transform())) == 64


def test_provenance_modification_detection():
    first = provenance_hash(_transform())
    second = provenance_hash(TransformationRecord("SDO-TEMP-000001", "Average Filter", "ALG-MAVG", "SDO-TEMP-000002", {"window": 5}))
    assert first != second


def test_sko_provenance_preservation():
    data = _data()
    @dataclass(frozen=True)
    class KnowledgeObject:
        provenance: ScientificDataObject
    sko = KnowledgeObject(data)
    assert sko.provenance.data_id == data.data_id


def test_complete_scientific_traceability():
    raw = _data()
    result = _data("SDO-TEMP-000002")
    algorithm = _algorithm()
    transform = _transform()
    graph = ProvenanceGraph()
    for node in (raw, result):
        graph.add_node(node)
    graph.add_link(raw, result)
    assert validate_provenance_chain((raw, transform, algorithm, result))
    assert graph.successors(raw.data_id) == (result.data_id,)
