/* Binary codec for the German DX saves. No browser or network dependencies. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory;
  else root.DXSave = factory(root.DX_DATA);
})(typeof globalThis === 'object' ? globalThis : this, function createCodec(data) {
  'use strict';
  const L = data.layout;
  const species = new Map(data.pokemon.map(p => [p.id, p]));
  const moves = new Map(data.moves.map(m => [m.id, m]));
  const items = new Map(data.items.map(i => [i.id, i]));
  const encodeMap = new Map(Object.entries(data.chars).filter(([, ch]) => [...ch].length === 1).map(([n, ch]) => [ch, +n]));
  const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
  const be16 = (a, i) => a[i] * 256 + a[i + 1];
  const put16 = (a, i, v) => { a[i] = v >> 8; a[i + 1] = v & 255; };
  const checksum = (bytes, start, end) => { let sum = 0; for (let i = start; i < end; i++) sum += bytes[i]; return (~sum) & 255; };
  const integer = (value, min, max) => Number.isInteger(value) && value >= min && value <= max;
  function decode(bytes) { let text = ''; for (const b of bytes) { if (b === 0x50) break; text += data.chars[b] ?? '�'; } return text; }
  function encode(text) {
    const chars = [...text];
    if (!chars.length || chars.length > 10) throw new Error('Ein Name muss 1–10 Zeichen enthalten.');
    const out = new Uint8Array(11).fill(0x50);
    chars.forEach((ch, i) => { if (!encodeMap.has(ch)) throw new Error(`Das Zeichen „${ch}“ kann das Spiel nicht darstellen.`); out[i] = encodeMap.get(ch); });
    return out;
  }
  function experience(growth, level) {
    const [numerator, denominator, square, linear, constant] = data.growthRates[growth];
    return Math.max(0, Math.floor(numerator * level ** 3 / denominator) + square * level ** 2 + linear * level - constant);
  }
  function stats(mon) {
    // Gen 1 applies accumulated stat experience only on a stat recalculation.
    // Preserve/display the saved values until the user changes a stat input.
    const old = mon.original;
    if (old && mon.species === old.species && mon.level === old.level && same(mon.dv, old.dv) && same(mon.effort, old.effort))
      return Array.from({length: 5}, (_, i) => be16(mon.raw, 34+i*2));
    const p = species.get(mon.species);
    if (!p) return [0, 0, 0, 0, 0];
    const [a, d, s, c] = mon.dv;
    const hp = (a & 1)*8 + (d & 1)*4 + (s & 1)*2 + (c & 1);
    return p.stats.map((base, i) => Math.floor(((base + [hp, a, d, s, c][i])*2 +
      Math.floor(Math.min(255, Math.ceil(Math.sqrt(mon.effort[i]))) / 4)) * mon.level / 100) +
      (i === 0 ? mon.level + 10 : 5));
  }
  function maxPP(move, ups = 0) { const base = moves.get(move)?.pp || 0; return base + Math.min(7, Math.floor(base / 5)) * ups; }
  function unpack(bytes, slot) {
    const raw = Array.from(bytes.slice(L.mons + slot*44, L.mons + (slot+1)*44));
    const nickname = Array.from(bytes.slice(L.nicknames + slot*11, L.nicknames + (slot+1)*11));
    const otName = Array.from(bytes.slice(L.otNames + slot*11, L.otNames + (slot+1)*11));
    const mon = { raw, nicknameRaw: nickname, otRaw: otName, species: raw[0], nickname: decode(nickname),
      level: raw[33], hp: be16(raw, 1), status: raw[4],
      dv: [raw[27] >> 4, raw[27] & 15, raw[28] >> 4, raw[28] & 15],
      effort: Array.from({length: 5}, (_, i) => be16(raw, 17 + 2*i)),
      moves: raw.slice(8, 12).map((id, i) => ({id, pp: raw[29+i] & 63, ups: raw[29+i] >> 6})) };
    mon.original = { species: mon.species, level: mon.level, nickname: mon.nickname,
      dv: [...mon.dv], effort: [...mon.effort], moves: structuredClone(mon.moves) };
    return mon;
  }
  function parse(input) {
    const bytes = new Uint8Array(input).slice();
    if (bytes.length !== 32768) throw new Error('Bitte einen normalen 32-KB-Spielstand (.sav) öffnen. Emulator-Schnellspeicherstände werden nicht unterstützt.');
    if (checksum(bytes, L.start, L.end) !== bytes[L.checksum]) throw new Error('Die Spielstand-Prüfsumme stimmt nicht. Bitte im Spiel erneut sichern und diese .sav öffnen.');
    const marker = String.fromCharCode(...bytes.slice(L.format, L.format + 2));
    if (marker[0] === 'I' && !['I1', 'I2'].includes(marker)) throw new Error('Diese Version des Spielstandformats wird noch nicht unterstützt.');
    const format = ['I1', 'I2'].includes(marker) ? marker : 'Original';
    if (format === 'I2') {
      if (data.featureMagic.some((b, i) => bytes[0x3600 + i] !== b) || bytes[0x3604] !== 1 || bytes[0x3605] !== 0 || bytes[0x3606] !== 2)
        throw new Error('Der DX-Erweiterungsblock fehlt oder hat eine unbekannte Version.');
      if (checksum(bytes, 0x3600, 0x3810) !== bytes[0x3810]) throw new Error('Die Prüfsumme der DX-Erweiterung stimmt nicht.');
    }
    const count = bytes[L.party];
    if (!integer(count, 1, 6) || bytes[L.party + 1 + count] !== 255) throw new Error('Die Teamliste im Spielstand ist ungültig.');
    const party = Array.from({length: count}, (_, i) => unpack(bytes, i));
    for (let i = 0; i < count; i++) {
      const m = party[i];
      if (!species.has(m.species) || bytes[L.party + 1 + i] !== m.species || !integer(m.level, 1, 100))
        throw new Error(`Teamplatz ${i+1} enthält ein nicht unterstütztes Pokémon oder Level.`);
    }
    const capacity = format === 'Original' ? 20 : 30;
    const bagCount = bytes[L.bag];
    if (bagCount > capacity || bytes[L.bag + 1 + bagCount*2] !== 255) throw new Error('Der Beutel im Spielstand ist ungültig.');
    const bag = Array.from({length: bagCount}, (_, i) => ({id: bytes[L.bag + 1 + i*2], count: bytes[L.bag + 2 + i*2]}));
    if (bag.some(item => item.id === 0 || item.id === 255)) throw new Error('Der Beutel enthält einen ungültigen Item-Eintrag.');
    const idOffset = L.playerId - (format === 'Original' ? 20 : 0);
    return { original: bytes, format, capacity, player: decode(bytes.slice(L.playerName, L.playerName + 11)),
      trainerId: be16(bytes, idOffset), playerNameRaw: Array.from(bytes.slice(L.playerName, L.playerName+11)), party, bag,
      originalBag: structuredClone(bag) };
  }
  function newMon(model, id = 0x54, level = 5) {
    const p = species.get(id);
    if (!p) throw new Error('Unbekannte Pokémon-Art.');
    const mon = { raw: Array(44).fill(0), nicknameRaw: Array(11).fill(0x50),
      otRaw: [...model.playerNameRaw], species: id, nickname: p.name, level, hp: 1,
      status: 0, dv: [15,15,15,15], effort: [0,0,0,0,0],
      moves: p.moves.map(id => ({id, pp: maxPP(id), ups: 0})), original: null };
    put16(mon.raw, 12, model.trainerId);
    mon.hp = stats(mon)[0];
    return mon;
  }
  function validate(model) {
    const errors = [];
    if (!integer(model.party.length, 1, 6)) errors.push('Das Team muss 1–6 Pokémon enthalten.');
    model.party.forEach((m, index) => {
      const prefix = `Teamplatz ${index + 1}: `;
      if (!species.has(m.species)) errors.push(prefix + 'Bitte eine gültige Pokémon-Art wählen.');
      if (!integer(m.level, 1, 100)) errors.push(prefix + 'Das Level muss zwischen 1 und 100 liegen.');
      if (!m.original || m.nickname !== m.original.nickname) { try { encode(m.nickname); } catch (e) { errors.push(prefix + e.message); } }
      if (m.dv.length !== 4 || m.dv.some(v => !integer(v, 0, 15))) errors.push(prefix + 'DVs müssen zwischen 0 und 15 liegen.');
      if (m.effort.length !== 5 || m.effort.some(v => !integer(v, 0, 65535))) errors.push(prefix + 'Trainingswerte müssen zwischen 0 und 65535 liegen.');
      const maximum = stats(m)[0];
      if (!integer(m.hp, 0, maximum)) errors.push(prefix + `KP müssen zwischen 0 und ${maximum} liegen.`);
      if (!integer(m.status, 0, 255)) errors.push(prefix + 'Ungültiger Status.');
      const seen = new Set(); let gap = false;
      if (m.moves.length !== 4) errors.push(prefix + 'Vier Attackenplätze werden benötigt.');
      m.moves.forEach((move, n) => {
        if (move.id === 0) { gap = true; if (move.pp || move.ups) errors.push(prefix + 'Leere Attacken dürfen keine AP haben.'); return; }
        if (!moves.has(move.id)) errors.push(prefix + `Unbekannte Attacke in Platz ${n+1}.`);
        if (gap) errors.push(prefix + 'Attacken bitte lückenlos von oben eintragen.');
        if (seen.has(move.id)) errors.push(prefix + 'Eine Attacke darf nicht doppelt vorkommen.');
        seen.add(move.id);
        if (!integer(move.ups, 0, 3) || !integer(move.pp, 0, maxPP(move.id, move.ups))) errors.push(prefix + `Ungültige AP in Attackenplatz ${n+1}.`);
      });
      if (!seen.size) errors.push(prefix + 'Bitte mindestens eine Attacke eintragen.');
    });
    if (model.bag.length > model.capacity) errors.push(`Der Beutel hat nur ${model.capacity} Plätze.`);
    const ids = new Set();
    model.bag.forEach((item, index) => {
      const original = model.originalBag.some(old => old.id === item.id);
      if (!items.has(item.id) && !original) errors.push(`Beutelplatz ${index+1}: Unbekanntes Item.`);
      if (!integer(item.count, 1, 99)) errors.push(`Beutelplatz ${index+1}: Die Menge muss 1–99 sein.`);
      if (ids.has(item.id)) errors.push(`Beutelplatz ${index+1}: Das Item ist bereits im Beutel.`);
      ids.add(item.id);
    });
    return [...new Set(errors)];
  }
  function exportSave(model) {
    const errors = validate(model);
    if (errors.length) throw new Error(errors.join('\n'));
    const out = model.original.slice();
    out[L.party] = model.party.length;
    model.party.forEach((m, index) => {
      const p = species.get(m.species), raw = Uint8Array.from(m.raw), old = m.original;
      const changedStats = !old || m.species !== old.species || m.level !== old.level || !same(m.dv, old.dv) || !same(m.effort, old.effort);
      raw[0] = m.species; put16(raw, 1, m.hp); raw[4] = m.status;
      if (changedStats) {
        raw[3] = raw[33] = m.level;
        if (!old || m.species !== old.species) { raw.set(p.types, 5); raw[7] = p.catchRate; }
        raw[27] = m.dv[0]*16 + m.dv[1]; raw[28] = m.dv[2]*16 + m.dv[3];
        m.effort.forEach((v, i) => put16(raw, 17+i*2, v));
        stats(m).forEach((v, i) => put16(raw, 34+i*2, v));
      }
      if (!old || m.species !== old.species || m.level !== old.level) {
        const exp = experience(p.growth, m.level);
        raw[14] = exp >> 16; raw[15] = (exp >> 8) & 255; raw[16] = exp & 255;
      }
      m.moves.forEach((move, i) => { raw[8+i] = move.id; raw[29+i] = move.ups*64 + move.pp; });
      out[L.party + 1 + index] = m.species;
      out.set(raw, L.mons + index*44);
      out.set(m.otRaw, L.otNames + index*11);
      out.set(old && m.nickname === old.nickname ? m.nicknameRaw : encode(m.nickname), L.nicknames + index*11);
      if (!old || m.species !== old.species) {
        const n = p.dex - 1;
        out[L.owned + (n >> 3)] |= 1 << (n & 7);
        out[L.seen + (n >> 3)] |= 1 << (n & 7);
      }
    });
    out[L.party + 1 + model.party.length] = 255;
    // Do not rewrite unused slots: a no-op export must be byte-identical.
    if (!same(model.bag, model.originalBag)) {
      out[L.bag] = model.bag.length;
      model.bag.forEach((item, i) => { out[L.bag + 1 + i*2] = item.id; out[L.bag + 2 + i*2] = item.count; });
      out[L.bag + 1 + model.bag.length*2] = 255;
    }
    out[L.checksum] = checksum(out, L.start, L.end);
    return out;
  }
  return { parse, exportSave, validate, stats, experience, newMon, maxPP, encode, decode, species, moves, items, checksum, layout: L };
});
