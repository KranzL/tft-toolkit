window.TFT = window.TFT || {};
(function () {
  const LABELS = Object.assign({}, TFT.riot.PLATFORM_LABELS, { cn: 'CN' });
  const state = { tab: 'comps', region: 'all', small: false, sort: 'share', open: new Set(), rank: localStorage.getItem('tft_rank') || 'master', running: false };
  let SNAP = null, NAMES = null, CLIENT = null;
  const $ = (s, el) => (el || document).querySelector(s);
  const h = (tag, attrs, ...kids) => { const el = document.createElement(tag); for (const [k, v] of Object.entries(attrs || {})) { if (k === 'class') el.className = v; else if (k.startsWith('on')) el.addEventListener(k.slice(2), v); else el.setAttribute(k, v); } for (const kid of kids.flat()) if (kid != null) el.append(kid.nodeType ? kid : document.createTextNode(String(kid))); return el; };
  const pct = (x, d = 1) => (x == null ? '' : (x * 100).toFixed(d) + '%');
  const num = (x, d = 2) => (x == null ? '' : Number(x).toFixed(d));
  const placeClass = p => (p == null ? '' : p <= 4.1 ? 'good' : p <= 4.6 ? 'mid' : 'bad');
  const placeTag = p => h('span', { class: 'place ' + placeClass(p) }, num(p));
  const unitChip = (name, extra) => h('span', { class: 'chip cost' + (NAMES.costOf(name) || '') }, name, extra ? h('span', { class: 'muted' }, extra) : null);
  const emblemChip = name => h('span', { class: 'chip emblem' }, name + ' Emblem');
  const setStatus = msg => { $('#status').textContent = msg; };
  function spark(points, key) {
    if (!points || points.length < 2) return h('span', { class: 'muted' }, '');
    const vals = points.map(p => p[key]); const max = Math.max(...vals, 0.0001), min = Math.min(...vals);
    const w = 96, hh = 26, pad = 2;
    const xs = points.map((p, i) => pad + i * (w - 2 * pad) / (points.length - 1));
    const ys = vals.map(v => hh - pad - (v - min) / (max - min || 1) * (hh - 2 * pad));
    const d = xs.map((x, i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + ys[i].toFixed(1)).join(' ');
    const area = d + ' L' + xs[xs.length - 1].toFixed(1) + ' ' + (hh - pad) + ' L' + xs[0].toFixed(1) + ' ' + (hh - pad) + ' Z';
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + hh); svg.setAttribute('class', 'spark'); svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'daily ' + key + ' from ' + points[0].date + ' to ' + points[points.length - 1].date);
    svg.innerHTML = '<path d="' + area + '" fill="currentColor" opacity="0.12"></path><path d="' + d + '" fill="none" stroke="currentColor" stroke-width="1.5"></path><circle cx="' + xs[xs.length - 1].toFixed(1) + '" cy="' + ys[ys.length - 1].toFixed(1) + '" r="2.2" fill="currentColor"></circle>';
    return svg;
  }
  function deltaTag(d) { const v = (d || 0) * 100; const cls = v > 0.15 ? 'up' : v < -0.15 ? 'down' : 'flat'; return h('span', { class: 'delta ' + cls, title: 'change in play share, last two days vs first two days' }, (v > 0 ? '+' : '') + v.toFixed(1) + ' pts'); }
  function regionsAvailable() {
    const set = new Set(); for (const c of SNAP.tactics.comps) for (const r of Object.keys(c.regions)) set.add(r);
    return ['na1', 'euw1', 'eun1', 'kr', 'jp1', 'br1', 'la1', 'la2', 'oc1', 'tr1', 'ru', 'me1', 'tw2', 'vn2', 'sg2'].filter(r => set.has(r));
  }
  function compsForView() {
    let comps = SNAP.tactics.comps.slice(); const r = state.region;
    if (!state.small) comps = comps.filter(c => c.share >= 0.004);
    if (r !== 'all') comps = comps.filter(c => c.regions[r] && c.regions[r].share > 0);
    const shareOf = c => (r === 'all' ? c.share : c.regions[r].share);
    const placeOf = c => (r === 'all' ? c.avg_place : c.regions[r].avg_place);
    const sorters = { share: (a, b) => shareOf(b) - shareOf(a), place: (a, b) => placeOf(a) - placeOf(b), top4: (a, b) => b.top4_rate - a.top4_rate, win: (a, b) => b.win_rate - a.win_rate, trend: (a, b) => (b.trend_delta || 0) - (a.trend_delta || 0) };
    comps.sort(sorters[state.sort] || sorters.share);
    return { comps, shareOf, placeOf };
  }
  function renderTiles() {
    const tt = SNAP.tactics, cn = SNAP.tencent, riot = SNAP.riot;
    const tiles = [
      { k: 'Global sample', v: tt.games.toLocaleString(), d: tt.rank_group + ' ranked games, patch ' + (tt.patch || '') },
      { k: 'Comps tracked', v: String(tt.comps.length), d: 'clusters with play data' },
      { k: 'China Master+', v: cn ? cn.comps.length + ' comps' : 'offline', d: cn ? 'Tencent data for patch ' + cn.patch + ', ' + cn.date : 'Tencent source unavailable' },
      { k: 'Your ladder sample', v: riot ? riot.boards.toLocaleString() + ' boards' : 'none yet', d: riot ? riot.matches + ' Master+ matches, last ' + riot.days + ' days' : 'add a Riot key in the Ladder tab' },
    ];
    $('#tiles').replaceChildren(...tiles.map(t => h('div', { class: 'tile' }, h('div', { class: 'k' }, t.k), h('div', { class: 'v' }, t.v), h('div', { class: 'd' }, t.d))));
  }
  function compDetail(c) {
    const r = state.region;
    const regionRows = Object.entries(c.regions).sort((a, b) => b[1].share - a[1].share).slice(0, 10);
    const maxShare = Math.max(...regionRows.map(x => x[1].share), 0.0001);
    const trend = r === 'all' ? c.trend : (c.region_trend[r] || []);
    return h('div', { class: 'detail-grid' },
      h('div', null, h('h4', null, 'Most played versions'), h('ul', { class: 'plain' }, c.variants.map(v => h('li', null, h('span', { class: 'chips' }, v.units.map(u => unitChip(u)), v.emblems.map(e => emblemChip(e))), h('span', { class: 'muted' }, ' ' + v.count + ' games, place ' + num(v.avg_place)))))),
      h('div', null, h('h4', null, 'Core units'), h('ul', { class: 'plain' }, c.core_units.slice(0, 10).map(u => h('li', null, unitChip(u.name, u.stars >= 3 ? ' 3-star' : u.stars === 2 ? ' 2-star' : ' 1-star'), h('span', { class: 'muted' }, ' in ' + pct(u.rate, 0) + ' of boards, place ' + num(u.avg_place)))))),
      h('div', null, h('h4', null, 'Win conditions'), h('ul', { class: 'plain' }, c.win_conditions.map(w => h('li', null, w.units.join(' + ') + ' ', h('span', { class: 'muted' }, w.count + ' games, place ' + num(w.avg_place))))),
        c.emblems.length ? h('div', null, h('h4', { style: 'margin-top:10px' }, 'Emblems seen'), h('div', { class: 'chips' }, c.emblems.map(([e]) => emblemChip(NAMES.traitFromEmblem(e))))) : null),
      h('div', null, h('h4', null, 'Where it is played'), h('div', { class: 'bars' }, regionRows.flatMap(([reg, s]) => [h('span', null, LABELS[reg] || reg), h('div', { class: 'bar' }, h('i', { style: 'width:' + (s.share / maxShare * 100).toFixed(0) + '%' })), h('span', { class: 'muted' }, pct(s.share) + ' / ' + num(s.avg_place))]))),
      h('div', null, h('h4', null, r === 'all' ? 'Daily share, all regions' : 'Daily share in ' + (LABELS[r] || r)), h('div', { style: 'color: var(--accent)' }, spark(trend, 'share')), h('ul', { class: 'plain', style: 'margin-top:6px' }, trend.map(t => h('li', { class: 'mono muted' }, t.date + '  ' + pct(t.share) + '  place ' + num(t.avg_place))))),
      h('div', null, h('h4', null, 'Top players on it'), h('ul', { class: 'plain' }, c.top_players.map(p => h('li', null, h('span', { class: 'chip' }, LABELS[p.region] || p.region), ' ' + p.name + (p.tag ? '#' + p.tag : ''), h('span', { class: 'muted' }, ' ' + p.avg_place_delta.toFixed(1) + ' pts better than field'))))));
  }
  function renderComps(main) {
    const { comps, shareOf, placeOf } = compsForView(); const r = state.region;
    const head = h('tr', null, h('th', null, 'Comp'), h('th', null, 'Board'), h('th', { class: 'num' }, r === 'all' ? 'Share' : LABELS[r] + ' share'), h('th', { class: 'num' }, r === 'all' ? 'Place' : LABELS[r] + ' place'), h('th', { class: 'num' }, 'Top 4'), h('th', { class: 'num' }, 'Win'), h('th', null, '7-day share'), h('th', { class: 'num' }, 'Change'));
    const body = h('tbody');
    for (const c of comps) {
      const id = c.code || c.name;
      body.append(h('tr', { class: 'comp' + (state.open.has(id) ? ' open' : '') },
        h('td', null, h('button', { class: 'row-toggle', 'aria-expanded': String(state.open.has(id)), onclick: () => { state.open.has(id) ? state.open.delete(id) : state.open.add(id); render(); } }, c.name), h('div', { class: 'muted', style: 'font-size:12px' }, c.traits.slice(0, 4).map(t => t.name + ' ' + t.tier).join(', '))),
        h('td', null, h('div', { class: 'chips' }, c.units.map(u => unitChip(u.name)))),
        h('td', { class: 'num' }, pct(shareOf(c))), h('td', { class: 'num' }, placeTag(placeOf(c))), h('td', { class: 'num' }, pct(c.top4_rate, 0)), h('td', { class: 'num' }, pct(c.win_rate, 0)),
        h('td', { style: 'color: var(--accent)' }, spark(r === 'all' ? c.trend : (c.region_trend[r] || []), 'share')), h('td', { class: 'num' }, deltaTag(c.trend_delta))));
      if (state.open.has(id)) body.append(h('tr', { class: 'detail' }, h('td', { colspan: 8 }, compDetail(c))));
    }
    main.append(h('section', null, h('h2', null, r === 'all' ? 'Comps across all regions' : 'Comps in ' + (LABELS[r] || r)),
      h('p', { class: 'lead' }, 'Source: tactics.tools, ' + SNAP.tactics.rank_group + ' ranked, patch ' + (SNAP.tactics.patch || '') + '. Share is the fraction of boards that match the cluster. Change compares the last two days of play share with the first two days in the window. Expand a comp for versions, emblems, region split and the players climbing on it.'),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, head), body))));
    const ranked = SNAP.tactics.comps.filter(c => c.share >= 0.005).sort((a, b) => (b.trend_delta || 0) - (a.trend_delta || 0));
    main.append(h('section', { class: 'grid2' },
      h('div', { class: 'card' }, h('h3', null, 'Rising this week'), h('ul', { class: 'plain' }, ranked.slice(0, 6).filter(c => c.trend_delta > 0).map(c => h('li', null, c.name + ' ', deltaTag(c.trend_delta), h('span', { class: 'muted' }, ' now ' + pct(c.share) + ', place ' + num(c.avg_place)))))),
      h('div', { class: 'card' }, h('h3', null, 'Falling this week'), h('ul', { class: 'plain' }, ranked.slice().reverse().slice(0, 6).filter(c => c.trend_delta < 0).map(c => h('li', null, c.name + ' ', deltaTag(c.trend_delta), h('span', { class: 'muted' }, ' now ' + pct(c.share) + ', place ' + num(c.avg_place)))))),
      h('div', { class: 'card' }, h('h3', null, 'Best placement, at least 1% share'), h('ul', { class: 'plain' }, SNAP.tactics.comps.filter(c => c.share >= 0.01).sort((a, b) => a.avg_place - b.avg_place).slice(0, 6).map(c => h('li', null, placeTag(c.avg_place), ' ' + c.name, h('span', { class: 'muted' }, ' ' + pct(c.share) + ' share')))))));
  }
  function renderRegions(main) {
    const cards = regionsAvailable().map(reg => {
      const comps = SNAP.tactics.comps.filter(c => c.regions[reg] && c.regions[reg].share >= 0.01).sort((a, b) => b.regions[reg].share - a.regions[reg].share);
      const distinct = SNAP.tactics.comps.filter(c => c.regions[reg] && c.share >= 0.005 && c.regions[reg].share / c.share >= 1.35).sort((a, b) => b.regions[reg].share / b.share - a.regions[reg].share / a.share).slice(0, 4);
      return h('div', { class: 'card' }, h('h3', null, LABELS[reg] || reg),
        h('ul', { class: 'plain' }, comps.slice(0, 7).map(c => h('li', null, placeTag(c.regions[reg].avg_place), ' ' + c.name, h('span', { class: 'muted' }, ' ' + pct(c.regions[reg].share))))),
        distinct.length ? h('div', null, h('h4', { class: 'sub-h' }, 'Played more here than elsewhere'), h('ul', { class: 'plain' }, distinct.map(c => h('li', null, c.name, h('span', { class: 'muted' }, ' ' + (c.regions[reg].share / c.share).toFixed(1) + 'x global share'))))) : null);
    });
    if (SNAP.tencent) cards.unshift(h('div', { class: 'card' }, h('h3', null, 'China (Tencent servers)'), h('ul', { class: 'plain' }, SNAP.tencent.comps.slice(0, 7).map(c => h('li', null, placeTag(c.avg_place), ' ' + c.name, h('span', { class: 'muted' }, ' ' + (c.raw.use_num || '') + ' games')))), h('p', { class: 'muted', style: 'margin:8px 0 0; font-size:12px' }, 'Master+ on the China servers is not on the Riot API. See the China tab for units, items and trait strength.')));
    main.append(h('section', null, h('h2', null, 'Region by region'), h('p', { class: 'lead' }, 'Top comps by play share inside each region, with the region-specific average placement. The distinctive list shows comps a region plays well above the global rate, which is usually where a regional trend starts.'), h('div', { class: 'grid2' }, cards)));
  }
  function renderUnitsTraits(main) {
    const g = SNAP.tactics.general;
    if (!g) { main.append(h('p', { class: 'note' }, 'Unit and trait stats were not available.')); return; }
    const traits = g.traits.filter(t => t.count >= 200).sort((a, b) => a.avg_place - b.avg_place);
    const units = g.units.filter(u => u.count >= 300).sort((a, b) => a.avg_place - b.avg_place);
    main.append(h('section', null, h('h2', null, 'Traits by tier'), h('p', { class: 'lead' }, 'Average placement of boards that had the trait active at that tier. Tier is the breakpoint index, so tier 1 is the first breakpoint. High tiers with few boards are usually prismatic tickets rather than a plan.'),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, h('tr', null, h('th', null, 'Trait'), h('th', { class: 'num' }, 'Tier'), h('th', { class: 'num' }, 'Boards'), h('th', { class: 'num' }, 'Place'), h('th', { class: 'num' }, 'Top 4'), h('th', { class: 'num' }, 'Win'))),
        h('tbody', null, traits.map(t => h('tr', null, h('td', null, t.name), h('td', { class: 'num' }, t.tier), h('td', { class: 'num' }, t.count.toLocaleString()), h('td', { class: 'num' }, placeTag(t.avg_place)), h('td', { class: 'num' }, num(t.top4, 0) + '%'), h('td', { class: 'num' }, num(t.win, 0) + '%'))))))));
    main.append(h('section', null, h('h2', null, 'Units'), h('p', { class: 'lead' }, 'Every unit with at least 300 boards in the sample, best placement first, with the items most often built on it.'),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, h('tr', null, h('th', null, 'Unit'), h('th', { class: 'num' }, 'Cost'), h('th', { class: 'num' }, 'Boards'), h('th', { class: 'num' }, 'Place'), h('th', { class: 'num' }, 'Top 4'), h('th', { class: 'num' }, 'Win'), h('th', null, 'Top items'), h('th', { class: 'num' }, '3-star place'))),
        h('tbody', null, units.map(u => h('tr', null, h('td', null, unitChip(u.name)), h('td', { class: 'num' }, u.cost || ''), h('td', { class: 'num' }, u.count.toLocaleString()), h('td', { class: 'num' }, placeTag(u.avg_place)), h('td', { class: 'num' }, num(u.top4, 0) + '%'), h('td', { class: 'num' }, num(u.win, 0) + '%'), h('td', null, h('div', { class: 'chips' }, u.top_items.map(i => h('span', { class: 'chip' }, i)))), h('td', { class: 'num' }, u.three_star_count >= 20 ? num(u.three_star_place) + ' (' + u.three_star_count + ')' : ''))))))));
    const emblems = (g.items || []).filter(i => /Emblem/.test(i.name)).sort((a, b) => a.avg_place - b.avg_place);
    if (emblems.length) main.append(h('section', null, h('h2', null, 'Emblems'), h('p', { class: 'lead' }, 'How boards holding each emblem placed. Pair this with the emblem planner when you get a spatula.'),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, h('tr', null, h('th', null, 'Emblem'), h('th', { class: 'num' }, 'Boards'), h('th', { class: 'num' }, 'Place'), h('th', { class: 'num' }, 'Top 4'), h('th', { class: 'num' }, 'Win'))),
        h('tbody', null, emblems.map(i => h('tr', null, h('td', null, emblemChip(i.name.replace(' Emblem', ''))), h('td', { class: 'num' }, i.count.toLocaleString()), h('td', { class: 'num' }, placeTag(i.avg_place)), h('td', { class: 'num' }, num(i.top4, 0) + '%'), h('td', { class: 'num' }, num(i.win, 0) + '%'))))))));
  }
  function renderChina(main) {
    const cn = SNAP.tencent;
    if (!cn) { main.append(h('p', { class: 'note' }, 'Tencent data was not reachable. It is fetched live from lol.qq.com when the page loads; try the Refresh button.')); return; }
    main.append(h('section', null, h('h2', null, 'China servers, ' + cn.tier), h('p', { class: 'lead' }, 'Tencent publishes Master+ statistics for the China servers on the official TFT site. These are grouped by main traits with the highest-placing builds per group, for patch ' + cn.patch + ' as of ' + cn.date + '.'),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, h('tr', null, h('th', null, 'Comp'), h('th', null, 'Board'), h('th', null, 'Carry and items'), h('th', { class: 'num' }, 'Games'), h('th', { class: 'num' }, 'Place'), h('th', { class: 'num' }, 'Top 4'), h('th', { class: 'num' }, 'Win'))),
        h('tbody', null, cn.comps.map(c => h('tr', null,
          h('td', null, h('strong', null, c.name), h('div', { class: 'muted', style: 'font-size:12px' }, c.sub_traits.slice(0, 4).map(([t, n]) => t + ' ' + n).join(', '))),
          h('td', null, h('div', { class: 'chips' }, c.units.map(u => unitChip(u)))),
          h('td', null, c.carry ? h('div', null, unitChip(c.carry), h('div', { class: 'chips', style: 'margin-top:4px' }, c.carry_items.map(i => h('span', { class: 'chip' }, i)))) : '', c.assist.length ? h('div', { style: 'margin-top:6px' }, unitChip(c.assist[0]), h('div', { class: 'chips', style: 'margin-top:4px' }, c.assist_items.map(i => h('span', { class: 'chip' }, i)))) : ''),
          h('td', { class: 'num' }, c.raw.use_num || ''), h('td', { class: 'num' }, placeTag(c.avg_place)), h('td', { class: 'num' }, pct(c.top4_rate, 0)), h('td', { class: 'num' }, pct(c.win_rate, 0)))))))));
    const traitRows = cn.traits.rows.map(r => ({ name: r.name, l: r.levels[0] })).filter(r => r.l && r.l.play_rate >= 0.003).sort((a, b) => a.l.avg_place - b.l.avg_place);
    main.append(h('section', { class: 'grid2' },
      h('div', { class: 'card' }, h('h3', null, 'Trait packages, best placement'), h('ul', { class: 'plain' }, traitRows.slice(0, 14).map(r => h('li', null, placeTag(r.l.avg_place), ' ' + r.name, h('span', { class: 'muted' }, ' ' + pct(r.l.play_rate) + ' of boards'))))),
      h('div', { class: 'card' }, h('h3', null, 'Units, best placement (at least 0.5% play)'), h('ul', { class: 'plain' }, cn.units.filter(u => u.play_rate >= 0.005).slice(0, 16).map(u => h('li', null, placeTag(u.avg_place), ' ', unitChip(u.name), h('span', { class: 'muted' }, ' top4 ' + pct(u.top4_rate, 0) + ', play ' + pct(u.play_rate))))))));
    if (cn.curated && cn.curated.length) main.append(h('section', null, h('h2', null, 'Lineups recommended by Chinese pros'), h('p', { class: 'lead' }, 'Curated boards published on the official China TFT site, with the early and mid boards their authors suggest.'),
      h('div', { class: 'grid2' }, cn.curated.map(l => h('div', { class: 'card' }, h('h3', null, l.name), h('div', { class: 'muted', style: 'font-size:12px' }, (l.author || '') + ', patch ' + (l.patch || '') + ', level ' + (l.level || '')),
        h('h4', { class: 'sub-h' }, 'Final board'), h('div', { class: 'chips' }, l.final.map(u => unitChip(u.name, u.stars >= 3 ? ' 3-star' : ''))),
        h('ul', { class: 'plain', style: 'margin-top:6px' }, l.final.filter(u => u.items.length).map(u => h('li', null, h('strong', null, u.name), h('span', { class: 'muted' }, ': ' + u.items.join(', '))))),
        l.early.length ? h('div', { style: 'margin-top:8px' }, h('span', { class: 'muted' }, 'Early: '), l.early.map(u => u.name).join(', ')) : null,
        l.mid.length ? h('div', null, h('span', { class: 'muted' }, 'Mid: '), l.mid.map(u => u.name).join(', ')) : null,
        l.three_star.length ? h('div', null, h('span', { class: 'muted' }, '3-star targets: '), l.three_star.join(', ')) : null,
        h('div', { class: 'chips', style: 'margin-top:6px' }, l.traits.map(t => h('span', { class: 'chip' }, t.name + ' ' + t.count))),
        l.notes.early ? h('p', { class: 'muted', style: 'font-size:12px; margin:8px 0 0' }, 'Author notes (Chinese): ' + l.notes.early + (l.notes.items ? ' / ' + l.notes.items : '')) : null)))));
  }
  function ladderPanel() {
    const key = TFT.riot.getKey();
    const plats = JSON.parse(localStorage.getItem('tft_riot_platforms') || '["na1","euw1","kr"]');
    const panel = h('div', { class: 'card' }, h('h3', null, 'Sample the ladders with your own Riot key'),
      h('p', { class: 'muted', style: 'margin:0 0 10px; font-size:13px' }, 'The key stays in this browser and is sent only to the Riot API through this site. A development key from developer.riotgames.com allows 100 requests every two minutes and expires after 24 hours, so keep the sample small: 15 players and 5 matches per region is about 100 requests per region.'),
      h('div', { class: 'form' },
        h('label', null, 'Riot API key ', h('input', { type: 'password', id: 'riotKey', value: key, placeholder: 'RGAPI-...', autocomplete: 'off' })),
        h('div', { class: 'chips', id: 'platChips' }, Object.keys(TFT.riot.PLATFORM_TO_REGION).map(p => h('label', { class: 'chip' }, h('input', { type: 'checkbox', value: p, checked: plats.includes(p) ? '' : null }), ' ' + LABELS[p]))),
        h('label', null, 'players per region ', h('input', { type: 'number', id: 'riotPlayers', value: localStorage.getItem('tft_riot_players') || 15, min: 1, max: 300 })),
        h('label', null, 'recent matches per player ', h('input', { type: 'number', id: 'riotMatches', value: localStorage.getItem('tft_riot_matches') || 5, min: 1, max: 20 })),
        h('div', { class: 'row' }, h('button', { class: 'btn primary', id: 'riotRun' }, state.running ? 'Stop' : 'Collect matches'), h('button', { class: 'btn', id: 'riotClear' }, 'Clear stored games'), h('span', { class: 'muted', id: 'riotProgress' }, ''))));
    for (const cb of panel.querySelectorAll('#platChips input')) if (!plats.includes(cb.value)) cb.checked = false;
    panel.querySelector('#riotClear').addEventListener('click', () => { TFT.riot.clearStore(); SNAP.riot = null; renderTiles(); render(); });
    panel.querySelector('#riotRun').addEventListener('click', () => runCollect(panel));
    return panel;
  }
  async function runCollect(panel) {
    if (state.running) { if (CLIENT) CLIENT.stopped = true; return; }
    const key = panel.querySelector('#riotKey').value.trim();
    if (!key) { panel.querySelector('#riotProgress').textContent = 'Paste a Riot API key first.'; return; }
    TFT.riot.setKey(key);
    const platforms = [...panel.querySelectorAll('#platChips input:checked')].map(i => i.value);
    const players = Number(panel.querySelector('#riotPlayers').value) || 15;
    const matches = Number(panel.querySelector('#riotMatches').value) || 5;
    localStorage.setItem('tft_riot_platforms', JSON.stringify(platforms)); localStorage.setItem('tft_riot_players', players); localStorage.setItem('tft_riot_matches', matches);
    state.running = true; panel.querySelector('#riotRun').textContent = 'Stop';
    const progress = panel.querySelector('#riotProgress');
    CLIENT = new TFT.riot.Client(key, msg => { progress.textContent = msg; });
    const store = TFT.riot.loadStore();
    try {
      const stats = await TFT.riot.collect(CLIENT, store, { platforms, players, matches, setNumber: NAMES.set.set, onProgress: msg => { progress.textContent = msg; } });
      progress.textContent = 'Done: ' + stats.new_matches + ' new matches in ' + stats.requests + ' requests.';
    } catch (e) {
      progress.textContent = e.message === 'stopped' ? 'Stopped.' : 'Failed: ' + e.message;
    }
    state.running = false;
    SNAP.riot = TFT.riot.buildSnapshot(TFT.riot.loadStore(), NAMES, 7);
    renderTiles(); render();
  }
  function renderLadder(main) {
    main.append(h('section', null, h('h2', null, 'Ladder players'), ladderPanel()));
    const riot = SNAP.riot;
    if (!riot) { main.append(h('p', { class: 'note' }, 'No ladder sample yet. Add a key and collect. The tool pulls every Challenger, Grandmaster and Master player for the regions you pick, samples the top of each ladder by LP, stores their recent ranked games in this browser and groups the boards here with per-player results.')); return; }
    main.append(h('section', null, h('h2', null, 'Boards from Master+ ladders, last ' + riot.days + ' days'), h('p', { class: 'lead' }, riot.boards.toLocaleString() + ' boards from ' + riot.matches.toLocaleString() + ' matches played by the top of each sampled ladder.'),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, h('tr', null, h('th', null, 'Archetype'), h('th', null, 'Common units'), h('th', { class: 'num' }, 'Boards'), h('th', { class: 'num' }, 'Share'), h('th', { class: 'num' }, 'Place'), h('th', { class: 'num' }, 'Top 4'), h('th', { class: 'num' }, 'Win'), h('th', null, 'Daily share'))),
        h('tbody', null, riot.comps.map(c => h('tr', null, h('td', null, h('strong', null, c.name), h('div', { class: 'muted', style: 'font-size:12px' }, 'carries: ' + c.carries.map(x => x[0]).join(', '))), h('td', null, h('div', { class: 'chips' }, c.units.slice(0, 9).map(u => unitChip(u.name, ' ' + pct(u.rate, 0))))), h('td', { class: 'num' }, c.count), h('td', { class: 'num' }, pct(c.share)), h('td', { class: 'num' }, placeTag(c.avg_place)), h('td', { class: 'num' }, pct(c.top4_rate, 0)), h('td', { class: 'num' }, pct(c.win_rate, 0)), h('td', { style: 'color: var(--accent)' }, spark(c.trend, 'share')))))))));
    const byPlatform = {}; for (const p of riot.players) (byPlatform[p.platform] = byPlatform[p.platform] || []).push(p);
    main.append(h('section', null, h('h2', null, 'Top players and what they are playing'), h('div', { class: 'grid2' }, Object.entries(byPlatform).map(([plat, rows]) => h('div', { class: 'card' }, h('h3', null, LABELS[plat] || plat),
      h('div', { class: 'tablewrap' }, h('table', null, h('thead', null, h('tr', null, h('th', null, 'Player'), h('th', { class: 'num' }, 'LP'), h('th', { class: 'num' }, 'Recent place'), h('th', null, 'Comps'))),
        h('tbody', null, rows.slice(0, 15).map(p => h('tr', null, h('td', null, p.name), h('td', { class: 'num' }, p.lp), h('td', { class: 'num' }, num(p.avg_place) + ' (' + p.games + ')'), h('td', null, p.comps.map(([c, n]) => c + ' x' + n).join('; '))))))))))));
  }
  function render() {
    if (!SNAP) return;
    const main = $('#main'); main.replaceChildren();
    const tabs = [['comps', 'Comps'], ['regions', 'Regions'], ['units', 'Units and traits'], ['china', 'China'], ['ladder', 'Ladder players']];
    $('#tabs').replaceChildren(...tabs.map(([id, label]) => h('button', { role: 'tab', 'aria-selected': String(state.tab === id), onclick: () => { state.tab = id; render(); } }, label)));
    const regs = ['all', ...regionsAvailable()];
    $('#regionSeg').replaceChildren(...regs.map(r => h('button', { 'aria-pressed': String(state.region === r), onclick: () => { state.region = r; render(); } }, r === 'all' ? 'All regions' : (LABELS[r] || r))));
    $('#regionSeg').hidden = state.tab !== 'comps'; $('#sortSel').parentElement.hidden = state.tab !== 'comps'; $('#showSmall').parentElement.hidden = state.tab !== 'comps';
    ({ comps: renderComps, regions: renderRegions, units: renderUnitsTraits, china: renderChina, ladder: renderLadder })[state.tab](main);
  }
  function renderHeader(sources) {
    const tt = SNAP.tactics;
    $('#subtitle').textContent = 'Set ' + SNAP.set + ' ' + SNAP.set_name + ', ' + tt.rank_group + ' ranked across all Riot regions plus China Master+. Data as of ' + SNAP.generated_at.replace('T', ' ').slice(0, 16) + ' UTC.';
    $('#sourceChips').replaceChildren(...sources.map(s => h('span', { class: 'chip' }, s)));
  }
  async function loadLive(rank) {
    const rg = TFT.tactics.RANK_GROUPS[rank] ?? 0;
    let patch; try { patch = await TFT.tactics.currentPatch(); } catch (e) { patch = { id: 'latest', label: null }; }
    const [raw, general] = await Promise.all([TFT.tactics.fetchComps(rg, patch.id), TFT.tactics.fetchGeneral(rg, patch.id).catch(() => null)]);
    const tt = TFT.tactics.normalize(raw, NAMES, rg, patch.id, patch.label);
    tt.general = general ? TFT.tactics.normalizeGeneral(general, NAMES) : null;
    return tt;
  }
  async function load(rank) {
    setStatus('Loading Set ' + (NAMES ? NAMES.set.set : '') + ' data...');
    const sources = [];
    let fallback = null;
    const getFallback = async () => { if (fallback === null) { try { fallback = await (await fetch('data/meta/latest.json')).json(); } catch (e) { fallback = false; } } return fallback; };
    const snap = { generated_at: new Date().toISOString(), set: NAMES.set.set, set_name: NAMES.set.set_name };
    setStatus('Loading tactics.tools ' + rank + ' sample...');
    try { snap.tactics = await loadLive(rank); sources.push('tactics.tools ' + snap.tactics.rank_group + ', patch ' + (snap.tactics.patch || snap.tactics.patch_id) + ', live'); }
    catch (e) { const fb = await getFallback(); if (fb && fb.tactics) { snap.tactics = fb.tactics; snap.generated_at = fb.generated_at; sources.push('tactics.tools snapshot from ' + fb.generated_at.slice(0, 10) + ' (live fetch failed: ' + e.message + ')'); } else { setStatus('Could not load comp data: ' + e.message); return null; } }
    setStatus('Loading China server data...');
    try { snap.tencent = await TFT.tencent.fetchAll(NAMES); sources.push('Tencent CN Master+, patch ' + snap.tencent.patch + ', live'); }
    catch (e) { const fb = await getFallback(); snap.tencent = fb && fb.tencent ? fb.tencent : null; sources.push(snap.tencent ? 'Tencent snapshot from ' + fb.generated_at.slice(0, 10) : 'Tencent offline'); }
    snap.riot = TFT.riot.buildSnapshot(TFT.riot.loadStore(), NAMES, 7);
    sources.push(snap.riot ? 'Riot API, your sample of ' + snap.riot.boards + ' boards' : 'Riot API sample not collected');
    setStatus('');
    return { snap, sources };
  }
  async function init() {
    const set = await (await fetch('data/set18.json')).json();
    NAMES = TFT.makeNames(set);
    $('#showSmall').addEventListener('change', e => { state.small = e.target.checked; render(); });
    $('#sortSel').addEventListener('change', e => { state.sort = e.target.value; render(); });
    const rankSel = $('#rankSel'); rankSel.value = state.rank;
    rankSel.addEventListener('change', async e => { state.rank = e.target.value; localStorage.setItem('tft_rank', state.rank); await reload(); });
    $('#refresh').addEventListener('click', async () => { localStorage.removeItem('tt_patch'); await reload(); });
    await reload();
  }
  async function reload() {
    const result = await load(state.rank);
    if (!result) return;
    SNAP = result.snap; renderHeader(result.sources); renderTiles(); render();
  }
  window.addEventListener('DOMContentLoaded', () => { init().catch(e => setStatus('Failed to start: ' + e.message)); });
})();
