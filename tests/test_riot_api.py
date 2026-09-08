import json

from tft_toolkit.meta.collect import collect
from tft_toolkit.meta.riot_api import RateLimiter, RiotClient
from tft_toolkit.meta.store import Store


def fake_match(mid, set_number=18, queue=1100):
    return {
        "metadata": {"match_id": mid, "participants": ["p1"]},
        "info": {
            "game_datetime": 1757000000000, "game_version": "Version 16.17.720.1234 (Sep 01 2026/12:00:00)",
            "tft_set_number": set_number, "queue_id": queue,
            "participants": [{
                "puuid": "p1", "placement": 1, "level": 8, "last_round": 34, "gold_left": 3,
                "units": [{"character_id": "DA_18_Ahri", "tier": 2, "itemNames": ["DA_Item_A"]}],
                "traits": [{"name": "DA_18_Blossom", "num_units": 5, "style": 2, "tier_current": 2, "tier_total": 5}],
                "augments": ["DA_Aug_1"],
            }],
        },
    }


def make_transport(calls):
    def transport(url):
        calls.append(url)
        headers = {"X-App-Rate-Limit": "20:1,100:120"}
        if "/tft/league/v1/challenger" in url:
            return 200, headers, json.dumps({"entries": [{"puuid": "p1", "leaguePoints": 1200, "wins": 50, "losses": 40}]})
        if "/tft/league/v1/" in url:
            return 200, headers, json.dumps({"entries": []})
        if "/ids" in url:
            return 200, headers, json.dumps(["NA1_1", "NA1_2", "NA1_3"])
        if "/matches/NA1_1" in url:
            return 200, headers, json.dumps(fake_match("NA1_1"))
        if "/matches/NA1_2" in url:
            return 200, headers, json.dumps(fake_match("NA1_2", queue=1090))
        if "/matches/NA1_3" in url:
            return 200, headers, json.dumps(fake_match("NA1_3", set_number=17))
        if "/riot/account/v1/" in url:
            return 200, headers, json.dumps({"gameName": "Tester", "tagLine": "NA1"})
        return 404, headers, ""
    return transport


def test_collect_filters_and_stores(tmp_path):
    calls = []
    client = RiotClient(api_key="x", transport=make_transport(calls))
    store = Store(tmp_path / "t.sqlite")
    stats = collect(client, store, platforms=["na1"], players_per_platform=5, matches_per_player=3, log=lambda m: None)
    assert stats["new_matches"] == 1
    assert stats["skipped"] == 2
    counts = store.counts()
    assert counts["matches"] == 1 and counts["boards"] == 1 and counts["players"] == 1
    boards = store.boards(set_number=18, queue_id=1100)
    assert boards[0]["patch"] == "16.17"
    assert store.players()[0]["game_name"] == "Tester"
    stats2 = collect(client, store, platforms=["na1"], players_per_platform=5, matches_per_player=3, log=lambda m: None)
    assert stats2["new_matches"] == 0


def test_rate_limiter_windows():
    rl = RateLimiter([(3, 0.2)])
    for _ in range(3):
        rl.wait()
    import time
    t0 = time.monotonic()
    rl.wait()
    assert time.monotonic() - t0 >= 0.15


def test_retry_after_on_429():
    seq = [(429, {"Retry-After": "0"}, ""), (200, {}, json.dumps({"entries": []}))]
    client = RiotClient(api_key="x", transport=lambda url: seq.pop(0))
    assert client.get("na1", "/tft/league/v1/master") == {"entries": []}
