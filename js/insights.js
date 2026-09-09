window.TFT = window.TFT || {};
TFT.insights = (function () {
  const MAJOR = ['na1', 'euw1', 'eun1', 'kr', 'jp1', 'br1', 'la1', 'la2', 'oc1', 'tr1', 'tw2', 'vn2', 'sg2'];
  function coverage(comps, regions) {
    const out = {};
    for (const r of regions) out[r] = comps.reduce((s, c) => s + ((c.regions[r] || {}).share || 0), 0);
    return out;
  }
  function reliableRegions(comps) {
    const regions = MAJOR.filter(r => comps.some(c => c.regions[r]));
    const cov = coverage(comps, regions);
    const max = Math.max(...Object.values(cov), 0.0001);
    return { regions: regions.filter(r => cov[r] >= 0.6 * max), coverage: cov };
  }
  function elsewhere(tactics, home, opts = {}) {
    const minElsewhere = opts.minElsewhere ?? 0.008;
    const minRatio = opts.minRatio ?? 1.5;
    const { regions, coverage: cov } = reliableRegions(tactics.comps);
    const others = regions.filter(r => r !== home);
    const rows = [];
    for (const c of tactics.comps) {
      const homeShare = (c.regions[home] || {}).share || 0;
      const homePlace = (c.regions[home] || {}).avg_place ?? null;
      let shareSum = 0, placeWeighted = 0, weight = 0;
      const per = [];
      for (const r of others) {
        const v = c.regions[r];
        const share = v ? v.share : 0;
        shareSum += share;
        if (v && share > 0) { placeWeighted += v.avg_place * share; weight += share; per.push([r, v]); }
      }
      if (!others.length) continue;
      const elsewhereShare = shareSum / others.length;
      const elsewherePlace = weight > 0 ? placeWeighted / weight : null;
      if (elsewhereShare < minElsewhere) continue;
      const ratio = homeShare > 0 ? elsewhereShare / homeShare : Infinity;
      if (ratio < minRatio) continue;
      per.sort((a, b) => b[1].share - a[1].share);
      const above = per.filter(([, v]) => v.share >= Math.max(homeShare * 1.5, 0.005)).length;
      rows.push({ comp: c, homeShare, homePlace, elsewhereShare, elsewherePlace, ratio, gap: elsewhereShare - homeShare, top: per.slice(0, 3), regionsAbove: above, regionsChecked: others.length });
    }
    rows.sort((a, b) => b.gap - a.gap);
    return { rows, regions: others, coverage: cov, home };
  }
  function jaccard(a, b) {
    const A = new Set(a), B = new Set(b);
    let inter = 0; for (const x of A) if (B.has(x)) inter += 1;
    return inter / (A.size + B.size - inter || 1);
  }
  function chinaOnly(tencent, tactics, threshold = 0.5) {
    if (!tencent) return [];
    const western = tactics.comps.filter(c => c.share >= 0.003).map(c => ({ c, units: c.units.map(u => u.name.split(' (')[0]) }));
    const out = [];
    for (const cn of tencent.comps) {
      const units = cn.units.map(u => u.split(' (')[0]);
      let best = null, bestSim = 0;
      for (const w of western) { const s = jaccard(units, w.units); if (s > bestSim) { bestSim = s; best = w.c; } }
      out.push({ comp: cn, closest: best, similarity: bestSim, distinct: bestSim < threshold });
    }
    return out.filter(x => x.distinct).sort((a, b) => a.comp.avg_place - b.comp.avg_place);
  }
  return { MAJOR, elsewhere, chinaOnly, reliableRegions };
})();
