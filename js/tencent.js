window.TFT = window.TFT || {};
TFT.tencent = (function () {
  const VERSION_CONFIG = 'https://game.gtimg.cn/images/lol/tfth5lib/v1/versionconfig.json';
  const PROXY = 'https://mlol.qt.qq.com/go/exploit/proxy';
  const CURATED = 'https://game.gtimg.cn/images/lol/act/tftzlkauto/json/lineupJson/{season}/62/lineup_detail_total.json';
  const TIER_PARTS = { all: '255', master: '0', diamond: '1', gold_emerald: '2', below_gold: '3' };
  const TIER_LABELS = { '255': 'All ranks', '0': 'Master+', '1': 'Diamond+', '2': 'Gold to Emerald', '3': 'Below Gold' };
  async function getJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error('tencent ' + res.status + ' ' + url);
    const raw = await res.text();
    try { return JSON.parse(raw); } catch (e) { const i = Math.min(...[raw.indexOf('{'), raw.indexOf('[')].filter(x => x >= 0)); return JSON.parse(raw.slice(i)); }
  }
  async function proxy(alias, params) {
    const res = await fetch(PROXY, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ req_alias: alias, is_return_source: 0, version_id: 'v1', req_params: params }) });
    if (!res.ok) throw new Error('tencent proxy ' + res.status);
    const data = await res.json();
    if (data.result !== 0) throw new Error('tencent proxy ' + alias + ' failed: ' + (data.msg || '') + ' ' + (data.err_msg || ''));
    return data;
  }
  async function loadIds(names) {
    const cfg = await getJson(VERSION_CONFIG);
    const current = cfg.find(c => (c.idSeason || '').startsWith('s18') && !(c.idSeason || '').includes('m')) || cfg[0];
    const [chess, race, job] = await Promise.all([getJson(current.urlChessData), getJson(current.urlRaceData), getJson(current.urlJobData)]);
    const chessMap = {}, chessCn = {}, traitMap = {};
    for (const c of chess.data || []) { const api = c.hero_EN_name || ''; chessMap[c.chessId] = api ? names.unit(api) : c.displayName; chessCn[c.chessId] = c.displayName; }
    for (const t of [...(race.data || []), ...(job.data || [])]) { const api = t.characterid || ''; traitMap[t.traitId] = api ? names.trait(api) : t.name; }
    return { season: current.idSeason, version: (current.arrVersionLimit || [null])[0], unit: id => chessMap[String(id)] || String(id), unitCn: id => chessCn[String(id)] || String(id), trait: id => traitMap[String(id)] || String(id), names };
  }
  async function fetchComps(ids, tier = 'master', timeType = 'v', queue = '1100') {
    const data = (await proxy('tft_lineup_group_list', { queue_id: queue, tier_part: TIER_PARTS[tier], time_type: timeType })).data;
    const comps = [];
    for (const entry of data.main_traits_data || []) {
      const mainTraits = (entry.main_trait_list || []).map(t => [ids.trait(t.trait_id), Number(t.chess_num)]);
      const info = entry.info || {};
      for (const row of info.list || []) {
        const carry = row.main_c_chess ? ids.unit(row.main_c_chess) : (info.main_c_chess_id ? ids.unit(info.main_c_chess_id) : null);
        comps.push({
          source: 'tencent', name: mainTraits.slice(0, 2).map(([t, n]) => t + ' ' + n).join(' + ') + (carry ? ' (' + carry + ')' : ''),
          main_traits: mainTraits, sub_traits: (row.sub_trait_list || []).map(t => [ids.trait(t.trait_id), Number(t.chess_num)]),
          units: (row.lineup || []).map(c => ids.unit(c)), core_units: (row.core_chess || []).map(c => ids.unit(c)), flex_units: (row.free_chess || []).map(c => ids.unit(c)),
          carry, carry_items: (row.main_c_chess_equip || []).map(i => ids.names.item(i)), assist: (row.assist_chess || []).map(c => ids.unit(c)), assist_items: (row.assist_chess_equip || []).map(i => ids.names.item(i)),
          avg_place: Number(row.avg_rank || 0), use_rate: row.use_rate != null ? Number(row.use_rate) : null, top4_rate: row.top_4_rate != null ? Number(row.top_4_rate) : null, win_rate: row.top_1_rate != null ? Number(row.top_1_rate) : null,
          raw: { use_num: row.use_num, lineup_rank: row.lineup_rank },
        });
      }
    }
    comps.sort((a, b) => (a.avg_place || 9) - (b.avg_place || 9));
    return { source: 'tencent', region: 'CN', tier: TIER_LABELS[TIER_PARTS[tier]], patch: data.period, date: data.dtstatdate, comps };
  }
  async function fetchUnits(ids, tier = 'master', timeType = 'v', queue = '1100') {
    const out = [];
    const results = await Promise.all([1, 2, 3, 4, 5].map(cost => proxy('tft_hero_ranking', { tier_part: TIER_PARTS[tier], base_price: String(cost), iqueue_id: queue, time_type: timeType }).then(r => [cost, r.data])));
    for (const [cost, data] of results) for (const row of data.details || []) {
      const hid = row.hero_id || ''; if (!(hid.startsWith('DA_') || ids.names.unitNames[hid])) continue;
      const s = (row.list || [{}])[0];
      out.push({ id: hid, name: ids.names.unit(hid), cost, avg_place: Number(s.avg_rank || 0), top4_rate: Number(s.top_4_rate || 0), win_rate: Number(s.top_1_rate || 0), play_rate: Number(s.use_rate || 0) });
    }
    out.sort((a, b) => (a.avg_place || 9) - (b.avg_place || 9));
    return out;
  }
  async function fetchTraits(ids, tier = 'master', queue = '1100') {
    const data = (await proxy('tft_trait_strength_trend', { tier_part: TIER_PARTS[tier], battletype: queue })).data;
    const rows = (data.main_buff_data || []).map(row => {
      const traits = (row.trait_list || []).map(t => [ids.trait(t.trait_id), Number(t.cycle || 0)]);
      const levels = [];
      for (let lvl = 1; lvl <= 5; lvl++) { const use = Number(row[lvl + '_use_rate'] || 0); if (use <= 0) continue; levels.push({ level: lvl, avg_place: Number(row[lvl + '_avg_rank'] || 0), top4_rate: Number(row[lvl + '_top_4_rate'] || 0), win_rate: Number(row[lvl + '_top_1_rate'] || 0), play_rate: use }); }
      return { traits, name: traits.map(([t, n]) => t + ' ' + n).join(' + '), levels };
    });
    return { date: data.dtstatdate, rows };
  }
  function heroes(rows, names) {
    return (rows || []).filter(h => h && typeof h === 'object' && (h.chess_type || 'hero') === 'hero').map(h => ({ name: names.unit(h.hero_id || ''), stars: h.numStar || 1, items: (h.equipment_id || '').split(',').filter(Boolean).map(i => names.item(i)), carry: !!h.is_carry_hero }));
  }
  async function fetchCurated(ids) {
    const data = await getJson(CURATED.replace('{season}', ids.season) + '?v=' + Math.floor(Date.now() / 3600000));
    return (data.lineup_list || []).map(l => {
      let detail = {}; try { detail = JSON.parse(l.detail || '{}'); } catch (e) {}
      return {
        name: detail.line_name || l.id, author: (l.lineupauthor_data || {}).name, quality: l.quality, patch: l.simulator_edition, updated: l.update_time, level: detail.needLevel,
        final: heroes(detail.hero_location, ids.names), early: heroes(detail.y21_early_heros, ids.names), mid: heroes(detail.y21_metaphase_heros, ids.names),
        three_star: (detail.level_3_heros || '').split(',').filter(Boolean).map(h => ids.names.unit(h)),
        traits: (detail.contact || []).filter(c => c && typeof c === 'object').map(c => ({ name: ids.names.trait(c.id || ''), count: c.num })),
        notes: { early: detail.early_info, items: detail.equipment_info },
      };
    });
  }
  async function fetchAll(names, tier = 'master') {
    const ids = await loadIds(names);
    const [comps, units, traits, curated] = await Promise.all([fetchComps(ids, tier), fetchUnits(ids, tier), fetchTraits(ids, tier), fetchCurated(ids).catch(() => [])]);
    return Object.assign(comps, { units, traits, curated });
  }
  return { loadIds, fetchComps, fetchUnits, fetchTraits, fetchCurated, fetchAll, TIER_PARTS };
})();
