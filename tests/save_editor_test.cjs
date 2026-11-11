/* node tests/save_editor_test.cjs — codec tests without browser dependencies. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'tools/save-editor/Pokemon-DX-Saveeditor.html'), 'utf8');
const data = JSON.parse(html.match(/globalThis.DX_DATA = (.*);\n/)[1]);
const C = require('../tools/save-editor/core.js')(data), L = C.layout;
function fix(b) { b[L.checksum] = C.checksum(b, L.start, L.end); return b; }
function fixture(format = 'I2') {
  const bytes = new Uint8Array(32768);
  bytes.set(C.encode('ROT'), L.playerName);
  bytes[L.format] = format === 'Original' ? 0 : 0x49;
  bytes[L.format+1] = format === 'Original' ? 0 : format.charCodeAt(1);
  const trainerId = L.playerId - (format === 'Original' ? 20 : 0);
  bytes[trainerId] = 0x12; bytes[trainerId+1] = 0x34;
  bytes.set(data.featureMagic, 0x3600); bytes[0x3604] = 1; bytes[0x3606] = 2;
  bytes[0x3610] = 1;
  for (let i = 112; i < 512; i++) bytes[0x3610+i] = (i*73) & 255;
  bytes[0x3810] = C.checksum(bytes, 0x3600, 0x3810);
  bytes[L.bag+1] = 255;
  const model = {original: bytes, capacity: format==='Original'?20:30, playerNameRaw: [...C.encode('ROT')],
    trainerId: 0x1234, format, bag: [], originalBag: [], party: []};
  model.party.push(C.newMon(model, 0x99, 5));
  return C.exportSave(model);
}
assert.equal(data.pokemon.length,151); assert.equal(data.moves.length,165);
assert.equal(C.species.get(0x54).name,'PIKACHU'); assert.equal(C.items.get(0x28).name,'SONDERBONBON');
assert.equal(C.experience(3,100),1059860); assert.equal(C.experience(4,100),800000);
assert.equal(C.experience(5,100),1250000); assert.equal(C.experience(3,1),0);
assert.equal(C.maxPP(45,3),61); // GROWL has base 40 PP; each PP Up adds at most 7.
for (const format of ['I2','I1','Original']) {
  const b = fixture(format), m = C.parse(b);
  assert.equal(m.format,format); assert.equal(m.trainerId,0x1234);
  assert.deepEqual(C.exportSave(m),b,`no-op export changed ${format}`);
  assert.equal(m.capacity,format==='Original'?20:30);
}
assert.deepEqual([...C.encode('Grün♀')].slice(0,5), [0x86,0xB1,0xD5,0xAD,0xF5]);
assert.equal(C.decode(C.encode('ÄÖÜäöüß♂')),'ÄÖÜäöüß♂');
assert.throws(()=>C.encode('😃'),/Zeichen/); assert.throws(()=>C.encode('ELFZEICHEN!'),/1–10/);
const original = fixture(), model = C.parse(original);
model.party[0].level = 100; model.party[0].effort.fill(65535);
model.party[0].hp = C.stats(model.party[0])[0]; model.party[0].nickname = 'BULBI';
assert.deepEqual(C.stats(model.party[0]),[293,196,196,188,228]);
model.party[0].moves[0] = {id:57, pp:15, ups:0}; // SURF
for(let i=0;i<5;i++) model.party.push(C.newMon(model,[0x54,0x15,0x5A,0xB0,0xB1][i],20+i));
model.bag = data.items.slice(0,30).map(i=>({id:i.id,count:99}));
const edited = C.exportSave(model), reload = C.parse(edited);
assert.equal(reload.party.length,6); assert.equal(reload.party[0].nickname,'BULBI');
assert.equal(reload.party[0].level,100); assert.equal(reload.party[0].hp,293);
assert.equal(reload.party[0].moves[0].id,57); assert.equal(reload.bag.length,30);
assert.equal(reload.party[1].raw[12]*256+reload.party[1].raw[13],0x1234);
assert.equal(C.decode(reload.party[1].otRaw),'ROT');
assert.deepEqual(edited.slice(0x3600,0x3811),original.slice(0x3600,0x3811),'feature bytes changed');
const allowed = i => i>=L.party && i<L.nicknames+66 || i>=L.bag && i<=L.bag+61 || i>=L.owned && i<L.seen+19 || i===L.checksum;
for(let i=0;i<edited.length;i++) if(edited[i]!==original[i]) assert(allowed(i),`unrelated byte changed at ${i.toString(16)}`);
assert(edited[L.owned+3] & 1,'new Pikachu was not registered');
// Reorder/remove retains each Pokemon's OT and nickname, not the old slot data.
reload.party.reverse(); reload.party.splice(2,1); reload.bag.splice(10,1);
const reordered=C.parse(C.exportSave(reload));
assert.equal(reordered.party.length,5); assert.equal(reordered.party[4].nickname,'BULBI');
assert.equal(reordered.bag.length,29); assert.equal(C.decode(reordered.party[0].otRaw),'ROT');
function invalid(change, pattern) { const m=C.parse(original); change(m); assert.throws(()=>C.exportSave(m),pattern); }
invalid(m=>m.party=[],/1–6/); invalid(m=>m.party[0].level=101,/Level/);
invalid(m=>m.party[0].dv[0]=16,/DVs/); invalid(m=>m.party[0].hp=9999,/KP/);
invalid(m=>m.party[0].moves[0].pp=64,/AP/);
invalid(m=>m.party[0].moves[1]={...m.party[0].moves[0]},/doppelt/);
invalid(m=>m.bag=[{id:40,count:100}],/1–99/);
invalid(m=>m.bag=[{id:40,count:1},{id:40,count:1}],/bereits/);
invalid(m=>m.bag=Array.from({length:31},(_,i)=>({id:data.items[i].id,count:1})),/30 Plätze/);
assert.throws(()=>C.parse(new Uint8Array(20)),/32-KB/);
let bad=original.slice();bad[L.party] ^= 1;assert.throws(()=>C.parse(bad),/Prüfsumme/);
bad=original.slice();bad[0x3680]^=1;assert.throws(()=>C.parse(bad),/DX-Erweiterung/);
bad=original.slice();bad[0x3604]=2;assert.throws(()=>C.parse(bad),/unbekannte Version/);
bad=original.slice();bad[L.format+1]=0x33;fix(bad);assert.throws(()=>C.parse(bad),/Version/);
bad=original.slice();bad[L.party]=7;fix(bad);assert.throws(()=>C.parse(bad),/Teamliste/);
fs.mkdirSync('/tmp/dx-editor-tests',{recursive:true});
fs.writeFileSync('/tmp/dx-editor-tests/original.sav',original);
fs.writeFileSync('/tmp/dx-editor-tests/edited.sav',edited);
if(process.env.DX_TEST_SAVE) {
  const real=new Uint8Array(fs.readFileSync(process.env.DX_TEST_SAVE)), m=C.parse(real);
  assert.deepEqual(C.exportSave(m),real,'real save no-op changed bytes');
  m.party[0].species=0x15; m.party[0].nickname='MEW';m.party[0].level=55;
  m.party[0].hp=C.stats(m.party[0])[0];m.party[0].status=0;
  m.party[0].moves=[{id:57,pp:15,ups:0},{id:94,pp:10,ups:0},{id:85,pp:15,ups:0},{id:135,pp:10,ups:0}];
  m.bag=m.bag.filter(i=>i.id!==40);if(m.bag.length===30)m.bag.pop();m.bag.push({id:40,count:99});
  const result=C.exportSave(m);assert.equal(C.parse(result).party[0].nickname,'MEW');
  fs.writeFileSync('/tmp/dx-editor-tests/real-edited.sav',result);
  console.log('PASS: real I2 save byte-identical roundtrip, edited team and 99 Rare Candies');
}
console.log('PASS: offline editor codec, all 151 species, Gen-1 stats/PP, formats, limits, checksums, preservation and reorder');
