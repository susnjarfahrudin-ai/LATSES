from lat_ces.agriculture.ministerial import build_official_snapshot


def test_agriculture_snapshot_has_all_three_scopes() -> None:
    snapshot = build_official_snapshot()
    assert {x.scope for x in snapshot.indicators} == {"BiH", "EU", "Svijet"}
    assert {x.scope for x in snapshot.evolution} == {"BiH", "EU", "Svijet"}


def test_agriculture_evolution_is_source_labelled() -> None:
    snapshot = build_official_snapshot()
    assert snapshot.evolution
    assert all(item.source and item.source_url and item.period for item in snapshot.evolution)
