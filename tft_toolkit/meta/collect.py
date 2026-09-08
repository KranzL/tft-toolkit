import time

from tft_toolkit.meta.riot_api import PLATFORM_TO_REGION, RANKED_QUEUE, RiotClient
from tft_toolkit.meta.store import Store

DEFAULT_PLATFORMS = ["na1", "euw1", "kr"]


def collect(client: RiotClient, store: Store, platforms=None, players_per_platform=60, matches_per_player=10,
            max_requests=None, set_number=18, ranked_only=True, resolve_names=True, log=print):
    platforms = platforms or DEFAULT_PLATFORMS
    started = client.requests_made
    stats = {"platforms": {}, "requests": 0, "new_matches": 0, "skipped": 0}

    def budget_left():
        if max_requests is None:
            return True
        return client.requests_made - started < max_requests

    for platform in platforms:
        if platform not in PLATFORM_TO_REGION:
            log(f"unknown platform {platform}, skipping")
            continue
        if not budget_left():
            break
        t0 = time.time()
        entries = client.ladder(platform)
        store.upsert_players(entries)
        sample = entries[:players_per_platform]
        log(f"[{platform}] ladder: {len(entries)} Master+ players, sampling top {len(sample)} by LP")
        new_here = 0
        for i, e in enumerate(sample, 1):
            if not budget_left():
                log(f"[{platform}] request budget reached")
                break
            ids = client.match_ids(platform, e["puuid"], count=matches_per_player)
            fresh = [m for m in ids if not store.has_match(m)]
            for mid in fresh:
                if not budget_left():
                    break
                match = client.match(platform, mid)
                if not match:
                    store.mark_seen(mid)
                    continue
                info = match.get("info", {})
                if set_number and info.get("tft_set_number") != set_number:
                    store.mark_seen(mid)
                    stats["skipped"] += 1
                    continue
                if ranked_only and info.get("queue_id") != RANKED_QUEUE:
                    store.mark_seen(mid)
                    stats["skipped"] += 1
                    continue
                store.add_match(platform, match)
                new_here += 1
            if resolve_names and budget_left():
                acct = client.account(platform, e["puuid"])
                if acct:
                    store.set_player_name(e["puuid"], acct.get("gameName"), acct.get("tagLine"))
            if i % 10 == 0:
                log(f"[{platform}] {i}/{len(sample)} players, {new_here} new matches, {client.requests_made - started} requests")
        stats["platforms"][platform] = {"players": len(sample), "new_matches": new_here, "seconds": round(time.time() - t0)}
        stats["new_matches"] += new_here
    stats["requests"] = client.requests_made - started
    return stats
