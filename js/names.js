window.TFT = window.TFT || {};
TFT.STYLE_NAMES = { 0: null, 1: 'bronze', 2: 'silver', 3: 'gold', 4: 'prismatic', 5: 'prismatic' };
TFT.STYLE_RANK = { null: 0, bronze: 1, silver: 2, gold: 3, unique: 2, prismatic: 4 };
TFT.makeNames = function (set) {
  const unitNames = {}, unitCost = {}, traitNames = {}, traitKind = {};
  for (const u of set.units) { unitNames[u.id] = u.name; unitCost[u.name] = u.cost; }
  for (const t of set.traits) { traitNames[t.id] = t.name; traitKind[t.name] = t.kind; }
  const emblemByItem = {};
  for (const t of set.traits) if (t.emblem) emblemByItem[t.emblem.id] = t.name;
  const luxForms = set.lux_forms || {};
  const items = set.items || {};
  function unit(id) {
    if (!id) return id;
    if (unitNames[id]) return unitNames[id];
    if (id in luxForms) return luxForms[id] ? 'Lux (' + luxForms[id] + ')' : 'Lux';
    if (id.includes('Lux')) return 'Lux';
    const tail = id.split('_').pop();
    for (const [uid, name] of Object.entries(unitNames)) if (uid.split('_').pop() === tail) return name;
    return id;
  }
  function trait(id) { return traitNames[id] || id; }
  function traitFromEmblem(itemId) { return emblemByItem[itemId] || (itemId || '').replace(/^DA_18_Emblem/, ''); }
  function item(id) {
    if (!id) return id;
    if (items[id]) return items[id];
    if (emblemByItem[id]) return emblemByItem[id] + ' Emblem';
    let name = id.replace(/^(DA_18_|DA_|TFT\d*_Item_|TFT_Item_)/, '').replace(/(Artifact_|Item_)/, '').replace('_Radiant', ' (Radiant)').replace('18', '');
    return name.replace(/([a-z])(?=[A-Z])/g, '$1 ');
  }
  function costOf(name) { return unitCost[(name || '').split(' (')[0]] || null; }
  return { set, unitNames, unitCost, traitNames, traitKind, unit, trait, traitFromEmblem, item, costOf };
};
