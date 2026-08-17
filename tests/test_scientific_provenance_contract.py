from lat_ces.scientific.provenance import ScientificProvenance


def test_scientific_provenance_preserves_legacy_ledger(tmp_path):
    path = tmp_path / "provenance.jsonl"
    provenance = ScientificProvenance(str(path))

    record = provenance.record(
        "MODEL_VERIFIED",
        {"status": "PASS"},
        source="test",
        model_id="SM-TEST",
        revision="A",
    )

    assert record.event == "MODEL_VERIFIED"
    assert record.model_id == "SM-TEST"
    history = provenance.history()
    assert len(history) == 1
    assert history[0]["event"] == "MODEL_VERIFIED"
    assert history[0]["metrics"]["status"] == "PASS"
