window.TFT = window.TFT || {};
TFT.tactics = (function () {
  const BOARDS_PER_GAME = 8;
  const RANK_GROUPS = { master: 0, diamond: 1, emerald: 2, platinum: 3, gm: 4 };
  const RANK_LABELS = { 0: 'Master+', 1: 'Diamond+', 2: 'Emerald+', 3: 'Platinum+', 4: 'Grandmaster+' };
  const PAGE_PROXY = 'api/ttpage/';
  const API = 'https://api.tft.tools/team-compositions/';
  const GENERAL = 'https://d3.tft.tools/stats2/general/1100/';
  const cacheGet = (k, ttl) => { try { const v = JSON.parse(localStorage.getItem(k) || 'null'); if (v && Date.now() - v.t < ttl) return v.d; } catch (e) {} return null; };
  const cacheSet = (k, d) => { try { localStorage.setItem(k, JSON.stringify({ t: Date.now(), d })); } catch (e) {} };
  async function currentPatch() {
    const cached = cacheGet('tt_patch', 6 * 3600 * 1000);
    if (cached) return cached;
    const res = await fetch(PAGE_PROXY);
    if (!res.ok) throw new Error('tactics.tools page ' + res.status);
    const html = await res.text();
    const m = html.match(/"patch":\{"_0":(\d+)\}/);
    if (!m) throw new Error('patch id not found on tactics.tools');
    const t = html.match(/<title>(.*?)<\/title>/);
    const pm = t ? t[1].match(/Patch ([0-9.]+[a-z]?)/) : null;
    const out = { id: Number(m[1]), label: pm ? pm[1] : null };
    cacheSet('tt_patch', out);
    return out;
  }
  async function fetchComps(rankGroup, patchId) {
    const res = await fetch(API + rankGroup + '/' + patchId);
    if (!res.ok) throw new Error('tactics.tools comps ' + res.status);
    return res.json();
  }
  async function fetchGeneral(rankGroup, patchId) {
    const res = await fetch(GENERAL + patchId + '/' + rankGroup);
    if (!res.ok) throw new Error('tactics.tools general stats ' + res.status);
    return res.json();
  }
  function compName(full, names) {
    const n = full.count || 1;
    const best = {};
    for (const [tid, tier, count] of full.traits || []) {
      const name = names.trait(tid); const w = (count / n) * (1 + 0.5 * tier);
      if (!best[name] || w > best[name]) best[name] = w;
    }
    const origins = Object.entries(best).filter(([nm]) => names.traitKind[nm] === 'origin').sort((a, b) => b[1] - a[1]);
    const classes = Object.entries(best).filter(([nm]) => names.traitKind[nm] === 'class').sort((a, b) => b[1] - a[1]);
    const prefix = origins.length && origins[0][1] >= 0.5 ? origins[0][0] : (classes.length ? classes[0][0] : 'Flex');
    const carries = (full.carryUnits || []).slice(0, 2).map(([u]) => names.unit(u));
    return carries.length ? prefix + ' ' + carries.join(' & ') : prefix;
  }
  function trendDelta(trend) {
    if (!trend || trend.length < 3) return 0;
    const head = trend.slice(0, 2), tail = trend.slice(-2);
    return tail.reduce((s, t) => s + t.share, 0) / tail.length - head.reduce((s, t) => s + t.share, 0) / head.length;
  }
  function normalize(data, names, rankGroup, patchId, patchLabel) {
    const total = data.count || 0;
    const comps = [];
    for (const grp of data.groups || []) {
      const full = grp.full; const n = full.count || 0; if (!n) continue;
      const best = (full.comps && full.comps[0]) || {};
      const units = []; const seen = new Set();
      for (const uid of best.units || []) { if (seen.has(uid)) continue; seen.add(uid); units.push({ id: uid, name: names.unit(uid) }); }
      const core = []; const seenCore = new Set();
      for (const [uid, tier, count, place] of (full.units || []).slice().sort((a, b) => b[2] - a[2])) { if (seenCore.has(uid)) continue; seenCore.add(uid); core.push({ id: uid, name: names.unit(uid), stars: tier, rate: count / n, avg_place: place }); if (core.length >= 12) break; }
      const traits = []; const seenT = new Set();
      for (const [tid, tier, count] of (full.traits || []).slice().sort((a, b) => b[1] - a[1] || b[2] - a[2])) { if (seenT.has(tid)) continue; seenT.add(tid); traits.push({ id: tid, name: names.trait(tid), tier, rate: count / n }); }
      const regions = {};
      for (const [region, perGame, place] of full.regionDistribution || []) if (perGame > 0) regions[region] = { share: perGame / BOARDS_PER_GAME, avg_place: place };
      const trend = (full.dateStats || []).slice().sort((a, b) => a[0].localeCompare(b[0])).map(([date, share, place]) => ({ date, share, avg_place: place }));
      const regionTrend = {};
      for (const [region, date, share, place] of full.regionDateStats || []) (regionTrend[region] = regionTrend[region] || []).push({ date, share, avg_place: place });
      for (const r of Object.values(regionTrend)) r.sort((a, b) => a.date.localeCompare(b.date));
      const players = (full.topPlayers || []).slice(0, 10).map(([region, name, v, tag]) => ({ region, name, avg_place_delta: v, tag }));
      const emblems = {};
      for (const comp of (full.spatComps || []).slice(0, 5)) for (const it of comp.spatItems || []) emblems[it] = (emblems[it] || 0) + (comp.count || 0);
      const comp = {
        source: 'tactics.tools', rank_group: RANK_LABELS[rankGroup] || String(rankGroup), name: compName(full, names), code: full.code,
        count: n, share: total ? n / total : 0, avg_place: full.place, top4_rate: n ? (full.top4 || 0) / n : 0, win_rate: n ? (full.win || 0) / n : 0, lp_delta: full.lpDelta,
        units, core_units: core, traits: traits.slice(0, 8),
        carries: (full.carryUnits || []).slice(0, 3).map(([u, w]) => ({ id: u, name: names.unit(u), weight: w })),
        win_conditions: (full.winCons || []).slice(0, 4).map(([cond, , count, place]) => ({ units: cond.map(x => names.unit(x.split('-')[0]) + (x.endsWith('-3') ? ' 3-star' : '')), count, avg_place: place })),
        regions, trend, region_trend: regionTrend, top_players: players,
        emblems: Object.entries(emblems).sort((a, b) => b[1] - a[1]).slice(0, 4),
        placement_distribution: full.placementDistribution,
        variants: (full.comps || []).slice(0, 4).map(c => ({ units: [...new Set(c.units || [])].map(u => names.unit(u)), emblems: (c.spatItems || []).map(e => names.traitFromEmblem(e)), count: c.count, avg_place: c.place })),
      };
      comp.trend_delta = trendDelta(trend);
      comps.push(comp);
    }
    comps.sort((a, b) => (a.avg_place ?? 9) - (b.avg_place ?? 9) || b.count - a.count);
    return { source: 'tactics.tools', rank_group: RANK_LABELS[rankGroup], patch_id: patchId, patch: patchLabel, games: total, comps };
  }
  function normalizeGeneral(data, names) {
    const units = Object.entries(data.units || {}).map(([uid, s]) => { const name = names.unit(uid); return { id: uid, name, cost: names.costOf(name), count: s.count, avg_place: s.place, top4: s.top4, win: s.won, top_items: (s.topItems || []).slice(0, 4).map(i => names.item(i)), three_star_count: s.starCount, three_star_place: s.starPlace }; });
    units.sort((a, b) => (a.avg_place ?? 9) - (b.avg_place ?? 9));
    const traits = Object.entries(data.traits || {}).map(([key, s]) => { const i = key.lastIndexOf('__'); const tid = key.slice(0, i); const tier = key.slice(i + 2); return { id: tid, name: names.trait(tid), tier: Number(tier) || tier, count: s.count, avg_place: s.place, top4: s.top4, win: s.won }; });
    traits.sort((a, b) => (a.avg_place ?? 9) - (b.avg_place ?? 9));
    const items = (data.items || []).map(it => ({ id: it.itemId, name: names.item(it.itemId), count: it.count, avg_place: it.place, top4: it.top4, win: it.won }));
    items.sort((a, b) => (a.avg_place ?? 9) - (b.avg_place ?? 9));
    return { total_entries: data.totalEntries, last_updated: data.lastUpdated, units, traits, items };
  }
  return { RANK_GROUPS, RANK_LABELS, currentPatch, fetchComps, fetchGeneral, normalize, normalizeGeneral, trendDelta };
})();
