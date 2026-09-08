window.TFT = window.TFT || {};
TFT.riot = (function () {
  const PLATFORM_TO_REGION = { na1: 'americas', br1: 'americas', la1: 'americas', la2: 'americas', euw1: 'europe', eun1: 'europe', tr1: 'europe', ru: 'europe', me1: 'europe', kr: 'asia', jp1: 'asia', oc1: 'sea', sg2: 'sea', tw2: 'sea', vn2: 'sea' };
  const PLATFORM_LABELS = { na1: 'NA', br1: 'BR', la1: 'LAN', la2: 'LAS', euw1: 'EUW', eun1: 'EUNE', tr1: 'TR', ru: 'RU', me1: 'ME', kr: 'KR', jp1: 'JP', oc1: 'OCE', sg2: 'SEA', tw2: 'TW', vn2: 'VN' };
  const RANKED_QUEUE = 1100;
  const STORE_KEY = 'tft_riot_store_v1';
  const KEY_KEY = 'tft_riot_api_key';
  const MAX_MATCHES = 600;
  const sleep = ms => new Promise(r => setTimeout(r, ms));

  class RateLimiter {
    constructor(limits) { this.limits = limits || [[20, 1000], [100, 120000]]; this.windows = this.limits.map(() => []); }
    updateFromHeader(header) {
      if (!header) return;
      const parsed = header.split(',').map(p => p.split(':').map(Number)).filter(x => x.length === 2 && x.every(Number.isFinite)).map(([c, s]) => [c, s * 1000]);
      if (parsed.length && JSON.stringify(parsed) !== JSON.stringify(this.limits)) { this.limits = parsed; this.windows = parsed.map(() => []); }
    }
    async wait() {
      for (;;) {
        const now = Date.now(); let delay = 0;
        this.limits.forEach(([count, ms], i) => { const w = this.windows[i]; while (w.length && w[0] <= now - ms) w.shift(); if (w.length >= count) delay = Math.max(delay, w[0] + ms - now); });
        if (delay <= 0) break;
        await sleep(delay + 50);
      }
      const now = Date.now(); for (const w of this.windows) w.push(now);
    }
  }

  class Client {
    constructor(key, log) { this.key = key; this.log = log || (() => {}); this.limiters = {}; this.requests = 0; this.stopped = false; }
    limiter(host) { return this.limiters[host] || (this.limiters[host] = new RateLimiter()); }
    async get(host, path, params) {
      let url = 'api/riot/' + host + path;
      if (params) url += '?' + new URLSearchParams(params).toString();
      const lim = this.limiter(host);
      for (let attempt = 0; attempt < 6; attempt++) {
        if (this.stopped) throw new Error('stopped');
        await lim.wait();
        const res = await fetch(url, { headers: { 'X-Riot-Token': this.key } });
        this.requests += 1;
        lim.updateFromHeader(res.headers.get('x-app-rate-limit'));
        if (res.status === 200) return res.json();
        if (res.status === 404) return null;
        if (res.status === 429) { const retry = Number(res.headers.get('retry-after') || 2); this.log('rate limited, waiting ' + retry + 's'); await sleep(retry * 1000 + 500); continue; }
        if (res.status === 401 || res.status === 403) throw new Error('Riot rejected the key (' + res.status + '). Development keys expire after 24 hours.');
        if (res.status >= 500) { await sleep(1500 * (attempt + 1)); continue; }
        throw new Error('Riot API ' + res.status + ' on ' + path);
      }
      throw new Error('gave up on ' + path);
    }
    async ladder(platform, tiers = ['challenger', 'grandmaster', 'master']) {
      const entries = [];
      for (const tier of tiers) {
        const data = await this.get(platform, '/tft/league/v1/' + tier, { queue: 'RANKED_TFT' });
        for (const e of (data && data.entries) || []) if (e.puuid) entries.push({ puuid: e.puuid, platform, tier: tier.toUpperCase(), lp: e.leaguePoints || 0, wins: e.wins || 0, losses: e.losses || 0 });
      }
      entries.sort((a, b) => b.lp - a.lp);
      return entries;
    }
    matchIds(platform, puuid, count) { return this.get(PLATFORM_TO_REGION[platform], '/tft/match/v1/matches/by-puuid/' + puuid + '/ids', { start: 0, count }).then(x => x || []); }
    match(platform, id) { return this.get(PLATFORM_TO_REGION[platform], '/tft/match/v1/matches/' + id); }
    account(platform, puuid) { return this.get(PLATFORM_TO_REGION[platform], '/riot/account/v1/accounts/by-puuid/' + puuid); }
  }

  function loadStore() { try { return JSON.parse(localStorage.getItem(STORE_KEY) || 'null') || { players: {}, matches: {}, seen: {} }; } catch (e) { return { players: {}, matches: {}, seen: {} }; } }
  function saveStore(store) {
    const ids = Object.keys(store.matches);
    if (ids.length > MAX_MATCHES) { ids.sort((a, b) => store.matches[a].d - store.matches[b].d); for (const id of ids.slice(0, ids.length - MAX_MATCHES)) delete store.matches[id]; }
    try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e) { console.warn('store full, dropping oldest matches'); const sorted = Object.keys(store.matches).sort((a, b) => store.matches[a].d - store.matches[b].d); for (const id of sorted.slice(0, Math.ceil(sorted.length / 4))) delete store.matches[id]; try { localStorage.setItem(STORE_KEY, JSON.stringify(store)); } catch (e2) {} }
  }
  function clearStore() { localStorage.removeItem(STORE_KEY); }
  function getKey() { return localStorage.getItem(KEY_KEY) || ''; }
  function setKey(k) { if (k) localStorage.setItem(KEY_KEY, k); else localStorage.removeItem(KEY_KEY); }
  function patchOf(version) { const m = (version || '').match(/(\d+\.\d+)/); return m ? m[1] : null; }
  function compactMatch(platform, match) {
    const info = match.info || {};
    return { p: platform, d: info.game_datetime || 0, v: patchOf(info.game_version), s: info.tft_set_number, q: info.queue_id,
      b: (info.participants || []).map(x => [x.puuid, x.placement, x.level, (x.units || []).map(u => [u.character_id, u.tier || 1, (u.itemNames || []).filter(Boolean)]), (x.traits || []).map(t => [t.name, t.num_units, t.style, t.tier_current, t.tier_total]), x.augments || []]) };
  }
  function boardsFrom(store, sinceMs, setNumber) {
    const out = [];
    for (const [id, m] of Object.entries(store.matches)) {
      if (sinceMs && m.d < sinceMs) continue;
      if (setNumber && m.s !== setNumber) continue;
      if (m.q !== RANKED_QUEUE) continue;
      for (const b of m.b) out.push({ match_id: id, platform: m.p, game_datetime: m.d, patch: m.v, puuid: b[0], placement: b[1], level: b[2], units: b[3].map(u => ({ character_id: u[0], tier: u[1], itemNames: u[2] })), traits: b[4].map(t => ({ name: t[0], num_units: t[1], style: t[2], tier_current: t[3], tier_total: t[4] })), augments: b[5] });
    }
    return out;
  }

  async function collect(client, store, opts) {
    const { platforms, players = 20, matches = 5, maxRequests = null, setNumber = 18, resolveNames = true, onProgress = () => {} } = opts;
    const started = client.requests;
    const stats = { new_matches: 0, skipped: 0, platforms: {} };
    const budget = () => maxRequests == null || client.requests - started < maxRequests;
    for (const platform of platforms) {
      if (!PLATFORM_TO_REGION[platform] || !budget() || client.stopped) continue;
      onProgress(platform + ': loading ladder');
      const entries = await client.ladder(platform);
      for (const e of entries) store.players[e.puuid] = Object.assign(store.players[e.puuid] || {}, e, { fetched: Date.now() });
      const sample = entries.slice(0, players);
      let fresh = 0;
      for (let i = 0; i < sample.length; i++) {
        if (!budget() || client.stopped) break;
        const e = sample[i];
        const ids = await client.matchIds(platform, e.puuid, matches);
        for (const mid of ids) {
          if (store.seen[mid] || !budget() || client.stopped) continue;
          const match = await client.match(platform, mid);
          store.seen[mid] = 1;
          if (!match) continue;
          const info = match.info || {};
          if ((setNumber && info.tft_set_number !== setNumber) || info.queue_id !== RANKED_QUEUE) { stats.skipped += 1; continue; }
          store.matches[mid] = compactMatch(platform, match);
          fresh += 1;
        }
        if (resolveNames && budget() && !store.players[e.puuid].name) { const acct = await client.account(platform, e.puuid); if (acct) store.players[e.puuid].name = (acct.gameName || 'unknown') + '#' + (acct.tagLine || ''); }
        onProgress(platform + ': ' + (i + 1) + '/' + sample.length + ' players, ' + fresh + ' new matches, ' + (client.requests - started) + ' requests');
        saveStore(store);
      }
      stats.platforms[platform] = { players: sample.length, new_matches: fresh };
      stats.new_matches += fresh;
    }
    saveStore(store);
    stats.requests = client.requests - started;
    return stats;
  }

  const STYLE_NAMES = { 0: null, 1: 'bronze', 2: 'silver', 3: 'gold', 4: 'prismatic', 5: 'prismatic' };
  const STYLE_RANK = { bronze: 1, silver: 2, gold: 3, unique: 2, prismatic: 4 };
  const mean = xs => xs.reduce((a, b) => a + b, 0) / (xs.length || 1);
  function archetypeOf(board, names) {
    const scored = [];
    for (const t of board.traits) {
      const style = STYLE_NAMES[t.style]; if (!style) continue;
      const name = names.trait(t.name); const kind = names.traitKind[name] || 'unique';
      let rank = STYLE_RANK[style] || 0; if (kind === 'unique') rank = Math.min(rank, 1.5);
      scored.push([rank, t.num_units || 0, name]);
    }
    scored.sort((a, b) => b[0] - a[0] || b[1] - a[1] || a[2].localeCompare(b[2]));
    const top = scored.slice(0, 2);
    if (!top.length) return ['No traits', []];
    return [top.map(([, n, name]) => name + ' ' + n).join(' + '), top.map(x => x[2])];
  }
  function carryOf(board, names) {
    let best = null;
    for (const u of board.units) { const key = [(u.itemNames || []).length, u.tier || 1, names.costOf(names.unit(u.character_id)) || 0]; if (!best || key[0] > best[0][0] || (key[0] === best[0][0] && (key[1] > best[0][1] || (key[1] === best[0][1] && key[2] > best[0][2])))) best = [key, u]; }
    return best && best[0][0] > 0 ? names.unit(best[1].character_id) : null;
  }
  function dayOf(ms) { return new Date(ms).toISOString().slice(0, 10); }
  function summarizeBoards(boards, names, minCount) {
    const groups = {};
    for (const b of boards) { const [label, traits] = archetypeOf(b, names); b._archetype = label; b._traits = traits; b._carry = carryOf(b, names); b._day = dayOf(b.game_datetime); (groups[label] = groups[label] || []).push(b); }
    const total = boards.length; const comps = [];
    const dayTotals = {}; for (const b of boards) dayTotals[b._day] = (dayTotals[b._day] || 0) + 1;
    for (const [label, items] of Object.entries(groups)) {
      if (items.length < minCount) continue;
      const n = items.length; const places = items.map(i => i.placement);
      const unitCount = {}, stars = {}, itemsBy = {}, carries = {}, augs = {}, regions = {}, days = {}, dayPlace = {}, levels = {};
      for (const i of items) {
        const seen = new Set();
        for (const u of i.units) { const name = names.unit(u.character_id); if (seen.has(name)) continue; seen.add(name); unitCount[name] = (unitCount[name] || 0) + 1; (stars[name] = stars[name] || {})[u.tier] = (stars[name][u.tier] || 0) + 1; for (const it of u.itemNames || []) { (itemsBy[name] = itemsBy[name] || {})[it] = (itemsBy[name][it] || 0) + 1; } }
        if (i._carry) carries[i._carry] = (carries[i._carry] || 0) + 1;
        for (const a of i.augments || []) augs[a] = (augs[a] || 0) + 1;
        regions[i.platform] = (regions[i.platform] || 0) + 1; days[i._day] = (days[i._day] || 0) + 1; (dayPlace[i._day] = dayPlace[i._day] || []).push(i.placement); levels[i.level] = (levels[i.level] || 0) + 1;
      }
      const topN = (obj, k) => Object.entries(obj).sort((a, b) => b[1] - a[1]).slice(0, k);
      comps.push({ name: label, traits: items[0]._traits, count: n, share: total ? n / total : 0, avg_place: mean(places), top4_rate: places.filter(p => p <= 4).length / n, win_rate: places.filter(p => p === 1).length / n,
        units: topN(unitCount, 12).map(([u, c]) => ({ name: u, rate: c / n, stars: stars[u], items: topN(itemsBy[u] || {}, 3).map(([k]) => names.item(k)) })),
        carries: topN(carries, 3), augments: topN(augs, 5), regions, levels,
        trend: Object.keys(days).sort().map(d => ({ date: d, count: days[d], share: days[d] / (dayTotals[d] || 1), avg_place: mean(dayPlace[d]) })) });
    }
    comps.sort((a, b) => a.avg_place - b.avg_place || b.count - a.count);
    return comps;
  }
  function traitStats(boards, names, minCount) {
    const rows = {};
    for (const b of boards) for (const t of b.traits) { const style = STYLE_NAMES[t.style]; if (!style) continue; const key = names.trait(t.name) + '|' + t.num_units + '|' + style; (rows[key] = rows[key] || []).push(b.placement); }
    return Object.entries(rows).filter(([, p]) => p.length >= minCount).map(([key, p]) => { const [trait, count, style] = key.split('|'); return { trait, count: Number(count), style, boards: p.length, avg_place: mean(p), top4_rate: p.filter(x => x <= 4).length / p.length }; }).sort((a, b) => a.avg_place - b.avg_place);
  }
  function unitStats(boards, names, minCount) {
    const rows = {};
    for (const b of boards) { const seen = new Set(); for (const u of b.units) { const name = names.unit(u.character_id); const key = name + '|' + (u.tier || 1); if (seen.has(key)) continue; seen.add(key); (rows[key] = rows[key] || []).push(b.placement); } }
    const n = boards.length || 1;
    return Object.entries(rows).filter(([, p]) => p.length >= minCount).map(([key, p]) => { const [unit, stars] = key.split('|'); return { unit, stars: Number(stars), cost: names.costOf(unit), boards: p.length, play_rate: p.length / n, avg_place: mean(p), top4_rate: p.filter(x => x <= 4).length / p.length }; }).sort((a, b) => a.avg_place - b.avg_place);
  }
  function playerStats(boards, players, recent = 10) {
    const by = {}; for (const b of boards) (by[b.puuid] = by[b.puuid] || []).push(b);
    const out = [];
    for (const p of Object.values(players)) {
      const games = (by[p.puuid] || []).sort((a, b) => b.game_datetime - a.game_datetime).slice(0, recent);
      if (!games.length) continue;
      const comps = {}; for (const g of games) if (g._archetype) comps[g._archetype] = (comps[g._archetype] || 0) + 1;
      out.push({ puuid: p.puuid, platform: p.platform, name: p.name || p.puuid.slice(0, 10), tier: p.tier, lp: p.lp, wins: p.wins, losses: p.losses, games: games.length, avg_place: mean(games.map(g => g.placement)), comps: Object.entries(comps).sort((a, b) => b[1] - a[1]).slice(0, 3) });
    }
    return out.sort((a, b) => a.platform.localeCompare(b.platform) || b.lp - a.lp);
  }
  function regionBreakdown(comps, boards) {
    const per = {}; for (const b of boards) per[b.platform] = (per[b.platform] || 0) + 1;
    const out = {};
    for (const [region, n] of Object.entries(per)) out[region] = { boards: n, top: comps.filter(c => (c.regions[region] || 0) >= 3).map(c => ({ name: c.name, count: c.regions[region], share: c.regions[region] / n })).sort((a, b) => b.count - a.count).slice(0, 8) };
    return out;
  }
  function buildSnapshot(store, names, days = 7) {
    const since = Date.now() - days * 86400000;
    const boards = boardsFrom(store, since, names.set.set);
    if (!boards.length) return null;
    const comps = summarizeBoards(boards, names, Math.max(4, Math.floor(boards.length / 150)));
    return { boards: boards.length, matches: Object.keys(store.matches).length, players_tracked: Object.keys(store.players).length, days, comps, traits: traitStats(boards, names, 5), units: unitStats(boards, names, 5), players: playerStats(boards, store.players), regions: regionBreakdown(comps, boards) };
  }
  return { PLATFORM_TO_REGION, PLATFORM_LABELS, Client, RateLimiter, loadStore, saveStore, clearStore, getKey, setKey, collect, buildSnapshot, boardsFrom };
})();
