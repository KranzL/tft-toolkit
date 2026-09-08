from tft_toolkit.meta.analyze import Names, archetype_of, summarize_boards, trait_stats, unit_stats


def board(placement, traits, units, platform="na1", day_ms=1757000000000):
    return {
        "match_id": "m", "platform": platform, "game_datetime": day_ms, "patch": "16.17", "puuid": "p",
        "placement": placement, "level": 8, "last_round": 30,
        "units": [{"character_id": u, "tier": 2, "itemNames": ["DA_Item_X"] if i == 0 else []} for i, u in enumerate(units)],
        "traits": [{"name": t, "num_units": n, "style": s, "tier_current": s, "tier_total": 4} for t, n, s in traits],
        "augments": ["DA_Aug"],
    }


def test_archetype_and_summary():
    names = Names()
    b = board(1, [("DA_18_Blossom", 5, 2), ("DA_18_Adaptor", 3, 2), ("DA_18_Caustic", 1, 4)], ["DA_18_MasterYi_AD", "DA_KogMaw18_AD", "DA_18_Lux_Fae"])
    label, traits = archetype_of(b, names)
    assert label == "Blossom 5 + Adaptor 3"
    boards = [board(p, [("DA_18_Blossom", 5, 2), ("DA_18_Adaptor", 3, 2)], ["DA_18_MasterYi_AD", "DA_Lux18_Blossom"]) for p in range(1, 9)]
    comps = summarize_boards(boards, names, min_count=2)
    assert comps[0]["name"] == "Blossom 5 + Adaptor 3"
    assert comps[0]["count"] == 8
    assert abs(comps[0]["avg_place"] - 4.5) < 1e-9
    assert comps[0]["units"][0]["name"] in ("Master Yi", "Lux")
    assert trait_stats(boards, names, min_count=2)[0]["trait"] in ("Blossom", "Adaptor")
    assert unit_stats(boards, names, min_count=2)[0]["unit"] in ("Master Yi", "Lux")
