import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque

PLATFORM_TO_REGION = {
    "na1": "americas", "br1": "americas", "la1": "americas", "la2": "americas",
    "euw1": "europe", "eun1": "europe", "tr1": "europe", "ru": "europe", "me1": "europe",
    "kr": "asia", "jp1": "asia",
    "oc1": "sea", "sg2": "sea", "tw2": "sea", "vn2": "sea",
}
PLATFORM_LABELS = {
    "na1": "NA", "br1": "BR", "la1": "LAN", "la2": "LAS", "euw1": "EUW", "eun1": "EUNE",
    "tr1": "TR", "ru": "RU", "me1": "ME", "kr": "KR", "jp1": "JP", "oc1": "OCE",
    "sg2": "SEA", "tw2": "TW", "vn2": "VN",
}
RANKED_QUEUE = 1100
DEFAULT_LIMITS = [(20, 1.0), (100, 120.0)]


class RiotApiError(Exception):
    def __init__(self, status, url, body=""):
        super().__init__(f"{status} {url} {body[:200]}")
        self.status = status
        self.url = url


class RateLimiter:
    def __init__(self, limits=None):
        self.limits = list(limits or DEFAULT_LIMITS)
        self.windows = [deque() for _ in self.limits]

    def update_from_header(self, header):
        if not header:
            return
        parsed = []
        for part in header.split(","):
            try:
                count, seconds = part.split(":")
                parsed.append((int(count), float(seconds)))
            except ValueError:
                continue
        if parsed and parsed != self.limits:
            self.limits = parsed
            self.windows = [deque() for _ in self.limits]

    def wait(self):
        while True:
            now = time.monotonic()
            delay = 0.0
            for (count, seconds), window in zip(self.limits, self.windows):
                while window and window[0] <= now - seconds:
                    window.popleft()
                if len(window) >= count:
                    delay = max(delay, window[0] + seconds - now)
            if delay <= 0:
                break
            time.sleep(delay + 0.05)
        now = time.monotonic()
        for window in self.windows:
            window.append(now)


class RiotClient:
    def __init__(self, api_key=None, limiter=None, transport=None, log=None):
        self.api_key = api_key or os.environ.get("RIOT_API_KEY")
        if not self.api_key:
            raise RuntimeError("RIOT_API_KEY is not set. Get a key at https://developer.riotgames.com and export RIOT_API_KEY=...")
        self.limiters = {}
        self.limiter_seed = limiter
        self.transport = transport or self._http_get
        self.log = log or (lambda msg: None)
        self.requests_made = 0

    def _limiter(self, host):
        if host not in self.limiters:
            self.limiters[host] = RateLimiter(self.limiter_seed.limits if self.limiter_seed else None)
        return self.limiters[host]

    def _http_get(self, url):
        req = urllib.request.Request(url, headers={"X-Riot-Token": self.api_key, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.status, dict(resp.headers), resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read().decode("utf-8", errors="replace")

    def get(self, host, path, params=None):
        url = f"https://{host}.api.riotgames.com{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        limiter = self._limiter(host)
        for attempt in range(6):
            limiter.wait()
            status, headers, body = self.transport(url)
            self.requests_made += 1
            limiter.update_from_header(headers.get("X-App-Rate-Limit") or headers.get("x-app-rate-limit"))
            if status == 200:
                return json.loads(body)
            if status == 404:
                return None
            if status == 429:
                retry = headers.get("Retry-After") or headers.get("retry-after") or "2"
                self.log(f"429 on {path}, sleeping {retry}s")
                time.sleep(float(retry) + 0.5)
                continue
            if status in (401, 403):
                raise RiotApiError(status, url, "API key rejected or expired (development keys last 24 hours)")
            if status >= 500:
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RiotApiError(status, url, body)
        raise RiotApiError(status, url, "gave up after retries")

    def ladder(self, platform, tiers=("challenger", "grandmaster", "master")):
        entries = []
        for tier in tiers:
            data = self.get(platform, f"/tft/league/v1/{tier}", {"queue": "RANKED_TFT"})
            if not data:
                continue
            for e in data.get("entries", []):
                entries.append({
                    "puuid": e.get("puuid"),
                    "summoner_id": e.get("summonerId"),
                    "platform": platform,
                    "tier": tier.upper(),
                    "lp": e.get("leaguePoints", 0),
                    "wins": e.get("wins", 0),
                    "losses": e.get("losses", 0),
                })
        entries = [e for e in entries if e["puuid"]]
        entries.sort(key=lambda e: -e["lp"])
        return entries

    def match_ids(self, platform, puuid, count=20, start=0):
        region = PLATFORM_TO_REGION[platform]
        return self.get(region, f"/tft/match/v1/matches/by-puuid/{puuid}/ids", {"start": start, "count": count}) or []

    def match(self, platform, match_id):
        region = PLATFORM_TO_REGION[platform]
        return self.get(region, f"/tft/match/v1/matches/{match_id}")

    def account(self, platform, puuid):
        region = PLATFORM_TO_REGION[platform]
        return self.get(region, f"/riot/account/v1/accounts/by-puuid/{puuid}")
