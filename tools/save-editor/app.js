(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const C = DXSave;
  let model = null, originalName = '', selected = 0, dirty = false, tab = 'team', originalState = '';
  const sortedSpecies = [...DX_DATA.pokemon].sort((a,b) => a.name.localeCompare(b.name, 'de'));
  const sortedMoves = [...DX_DATA.moves].sort((a,b) => a.name.localeCompare(b.name, 'de'));
  const sortedItems = [...DX_DATA.items].sort((a,b) => a.name.localeCompare(b.name, 'de'));
  function el(tag, props = {}, children = []) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(props)) {
      if (key === 'text') node.textContent = value;
      else if (key.startsWith('on')) node.addEventListener(key.slice(2), value);
      else if (key === 'class') node.className = value;
      else if (key.startsWith('aria-')) node.setAttribute(key, value);
      else node[key] = value;
    }
    for (const child of children) node.append(child);
    return node;
  }
  function message(text, error = false) {
    $('message').textContent = text; $('message').className = 'message' + (error ? ' error' : ''); $('message').hidden = !text;
  }
  function option(value, text, disabled = false) { return el('option', {value, text, disabled}); }
  function field(text, input, help) {
    const label = el('label', {class: 'field'}, [el('span', {class: 'label', text}), input]);
    if (help) label.append(el('span', {class: 'help', text: help}));
    return label;
  }
  function number(value, min, max, label, change) {
    return el('input', {type: 'number', value, min, max, 'aria-label': label, onchange: e => { change(e.target.value === '' ? NaN : Number(e.target.value)); }});
  }
  function select(options, value, label, change) {
    const node = el('select', {'aria-label': label, onchange: e => change(Number(e.target.value))}, options);
    node.value = value;
    return node;
  }
  function mark() { dirty = true; refreshStatus(); }
  function refreshStatus() {
    if (!model) return;
    $('team-count').textContent = model.party.length + ' / 6';
    $('bag-count').textContent = model.bag.length + ' / ' + model.capacity;
    $('file-status').textContent = dirty ? '● Ungespeicherte Änderungen' : 'Originaldatei bleibt unverändert';
    $('reset').disabled = originalState === JSON.stringify({party: model.party, bag: model.bag});
    const errors = C.validate(model);
    $('download').disabled = errors.length > 0;
    const box = $('validation'); box.replaceChildren(); box.hidden = !errors.length;
    if (errors.length) box.append(el('strong', {text: 'Vor dem Speichern bitte korrigieren:'}), el('ul', {}, errors.map(text => el('li', {text}))));
  }
  function heal(mon) {
    mon.hp = C.stats(mon)[0]; mon.status = 0;
    mon.moves.forEach(m => m.pp = C.maxPP(m.id, m.ups));
  }
  function clampHP(mon) { const hp = C.stats(mon)[0]; if (Number.isFinite(hp)) mon.hp = Math.min(mon.hp, Math.max(0, hp)); }
  function renderParty() {
    const list = $('party-list'); list.replaceChildren();
    list.append(el('p', {class: 'team-caption', text: 'Wähle einen Teamplatz zum Bearbeiten.'}));
    model.party.forEach((mon, i) => {
      const p = C.species.get(mon.species);
      const button = el('button', {class: 'mon-card', 'aria-pressed': String(i === selected),
        'aria-label': `Teamplatz ${i+1}: ${mon.nickname}, Level ${mon.level}`,
        onclick: () => { selected = i; renderParty(); renderMon(); }}, [
        el('span', {class: 'slot-num', text: String(i+1).padStart(2, '0')}),
        el('img', {src: p.image, alt: '', width: 56, height: 56}),
        el('span', {}, [el('strong', {text: mon.nickname}), el('span', {class: 'sub', text: `${p.name} · Lv. ${mon.level}`})])
      ]);
      list.append(button);
    });
    list.append(el('button', {class: 'add-mon', text: '+ Pokémon hinzufügen', disabled: model.party.length >= 6,
      onclick: () => { model.party.push(C.newMon(model)); selected = model.party.length - 1; mark(); renderParty(); renderMon(); }}));
  }
  function renderMon() {
    const mon = model.party[selected], p = C.species.get(mon.species), panel = $('mon-editor');
    panel.replaceChildren();
    const moveMon = delta => { const to = selected + delta; [model.party[selected], model.party[to]] = [model.party[to], model.party[selected]]; selected = to; mark(); renderParty(); renderMon(); };
    panel.append(el('div', {class: 'panel-header'}, [el('div', {}, [el('h2', {text: `Teamplatz ${selected+1}`}),
      el('p', {class: 'caption', text: `Pokédex #${String(p.dex).padStart(3, '0')}`})]),
      el('div', {class: 'actions'}, [
        el('button', {class: 'icon', text: '↑', 'aria-label': 'Pokémon nach oben', disabled: selected === 0, onclick: () => moveMon(-1)}),
        el('button', {class: 'icon', text: '↓', 'aria-label': 'Pokémon nach unten', disabled: selected === model.party.length-1, onclick: () => moveMon(1)}),
        el('button', {class: 'small danger', text: 'Entfernen', disabled: model.party.length <= 1, onclick: () => {
          model.party.splice(selected, 1); selected = Math.min(selected, model.party.length-1); mark(); renderParty(); renderMon();
        }})
      ])]));
    const speciesSelect = select(sortedSpecies.map(s => option(s.id, `${s.name} · #${String(s.dex).padStart(3, '0')}`)), mon.species, 'Pokémon-Art', id => {
      const previous = C.species.get(mon.species);
      mon.species = id;
      if (mon.nickname === previous.name) mon.nickname = C.species.get(id).name;
      clampHP(mon); mark(); renderParty(); renderMon();
    });
    panel.append(el('div', {class: 'fields'}, [field('Pokémon-Art', speciesSelect),
      field('Level', number(mon.level, 1, 100, 'Level', value => { mon.level = value; clampHP(mon); mark(); renderParty(); renderMon(); }))]));
    const name = el('input', {type: 'text', value: mon.nickname, maxLength: 10, spellcheck: false, 'aria-label': 'Spitzname',
      oninput: e => { mon.nickname = e.target.value.normalize('NFC'); mark(); renderParty(); }});
    const stats = C.stats(mon), names = ['KP', 'ANGRIFF', 'VERTEIDIGUNG', 'INITIATIVE', 'SPEZIAL'];
    panel.append(el('div', {style: 'margin-top:16px'}, [field('Spitzname', name, 'Bis zu 10 Zeichen. Groß- und Kleinbuchstaben sowie deutsche Umlaute sind möglich.') ]));
    panel.append(el('div', {class: 'stats'}, stats.map((value, i) => el('div', {class: 'stat'}, [el('span', {text: names[i]}), el('strong', {text: Number.isFinite(value) ? String(value) : '–'})]))));
    const statuses = [[0,'Gesund'],[1,'Schlaf · 1 Runde'],[2,'Schlaf · 2 Runden'],[3,'Schlaf · 3 Runden'],[4,'Schlaf · 4 Runden'],[5,'Schlaf · 5 Runden'],[6,'Schlaf · 6 Runden'],[7,'Schlaf · 7 Runden'],[8,'Vergiftet'],[16,'Verbrennung'],[32,'Eingefroren'],[64,'Paralysiert']];
    if (!statuses.some(s => s[0] === mon.status)) statuses.push([mon.status, `Gespeicherter Status 0x${mon.status.toString(16)}`]);
    panel.append(el('div', {class: 'section-heading'}, [el('h3', {text: 'Zustand'}), el('button', {class: 'small', text: 'Heilen & AP auffüllen', onclick: () => { heal(mon); mark(); renderMon(); }})]));
    panel.append(el('div', {class: 'health-grid'}, [field(`Aktuelle KP / ${stats[0]}`, number(mon.hp, 0, stats[0], 'Aktuelle KP', v => { mon.hp = v; mark(); })),
      field('Status', select(statuses.map(([id, name]) => option(id, name)), mon.status, 'Status', v => { mon.status = v; mark(); }))]));
    panel.append(el('div', {class: 'section-heading'}, [el('h3', {text: 'Attacken'}), el('span', {class: 'caption', text: 'AP = Angriffspunkte'})]));
    panel.append(el('div', {class: 'move-labels', 'aria-hidden': 'true'}, [el('span', {text: 'Attacke'}), el('span', {text: 'AP'}), el('span', {text: 'AP-Plus'})]));
    mon.moves.forEach((move, i) => {
      const choice = select([option(0, '— Keine Attacke'), ...sortedMoves.map(m => option(m.id, m.name))], move.id, `Attacke ${i+1}`, id => {
        mon.moves[i] = {id, ups: 0, pp: C.maxPP(id)};
        const active = mon.moves.filter(m => m.id !== 0);
        mon.moves = [...active, ...Array.from({length: 4-active.length}, () => ({id:0,pp:0,ups:0}))];
        mark(); renderMon();
      });
      const pp = number(move.pp, 0, C.maxPP(move.id, move.ups), `AP Attacke ${i+1}`, v => { move.pp = v; mark(); });
      pp.disabled = !move.id;
      const ups = select([0,1,2,3].map(v => option(v, `${v} / 3`)), move.ups, `AP-Plus Attacke ${i+1}`, v => {
        move.ups = v; move.pp = Math.min(move.pp, C.maxPP(move.id, v)); mark(); renderMon();
      }); ups.disabled = !move.id;
      panel.append(el('div', {class: 'move-row'}, [choice, el('div', {}, [pp, el('div', {class: 'max', text: `max. ${C.maxPP(move.id, move.ups)}`})]), ups]));
    });
    const advanced = el('details', {}, [el('summary', {text: 'DVs & Trainingswerte'})]);
    advanced.append(el('p', {class: 'footnote', text: 'DVs sind die individuellen Werte (0–15). Der KP-DV ergibt sich aus den vier anderen DVs. Trainingswerte entsprechen der Stat-Erfahrung der ersten Generation (0–65535).'}));
    advanced.append(el('div', {class: 'advanced-grid'}, ['Angriff','Verteidigung','Initiative','Spezial'].map((label,i) => field(`${label}-DV`, number(mon.dv[i], 0, 15, `${label}-DV`, v => { mon.dv[i] = v; clampHP(mon); mark(); renderMon(); })))));
    advanced.append(el('div', {class: 'advanced-grid five'}, ['KP','Angriff','Verteidigung','Initiative','Spezial'].map((label,i) => field(label, number(mon.effort[i], 0, 65535, `${label}-Training`, v => { mon.effort[i] = v; clampHP(mon); mark(); renderMon(); })))));
    panel.append(advanced, el('p', {class: 'footnote', text: 'Statuswerte werden passend zu Art, Level, DVs und Training berechnet. Ein geändertes Level setzt die Erfahrung auf dessen Anfangswert. Attacken dürfen frei gewählt werden. Neue Arten werden im Pokédex als gesehen und gefangen eingetragen.'}));
  }
  function renderBag() {
    const used = new Set(model.bag.map(i => i.id));
    const add = $('add-item'); const previous = Number(add.value); add.replaceChildren(...sortedItems.filter(i => !used.has(i.id)).map(i => option(i.id, i.name)));
    if ([...add.options].some(o => +o.value === previous)) add.value = previous;
    const full = model.bag.length >= model.capacity;
    $('add-bag').disabled = full || !add.options.length; add.disabled = full;
    $('add-count').disabled = full; $('sort-bag').disabled = model.bag.length < 2;
    const list = $('bag-list'); list.replaceChildren();
    if (!model.bag.length) list.append(el('p', {class: 'empty', text: 'Dein Beutel ist leer. Füge oben ein Item hinzu.'}));
    model.bag.forEach((item, i) => {
      const options = sortedItems.map(o => option(o.id, o.name, used.has(o.id) && o.id !== item.id));
      if (!C.items.has(item.id)) options.unshift(option(item.id, `Gespeichertes Item 0x${item.id.toString(16)}`));
      const reorder = delta => { [model.bag[i], model.bag[i+delta]] = [model.bag[i+delta], model.bag[i]]; mark(); renderBag(); };
      list.append(el('div', {class: 'bag-row'}, [
        el('span', {class: 'row-index', text: String(i+1).padStart(2,'0')}),
        select(options, item.id, `Item Beutelplatz ${i+1}`, id => { item.id = id; mark(); renderBag(); }),
        number(item.count, 1, 99, `Menge Beutelplatz ${i+1}`, value => { item.count = value; mark(); }),
        el('div', {class: 'row-actions'}, [
          el('button', {class:'icon',text:'↑','aria-label':`Item ${i+1} nach oben`,disabled:i===0,onclick:()=>reorder(-1)}),
          el('button', {class:'icon',text:'↓','aria-label':`Item ${i+1} nach unten`,disabled:i===model.bag.length-1,onclick:()=>reorder(1)}),
          el('button', {class:'icon danger',text:'×','aria-label':`Item ${i+1} entfernen`,onclick:()=>{model.bag.splice(i,1);mark();renderBag();}})
        ])]));
    });
  }
  function switchTab(value) {
    tab = value;
    for (const key of ['team','bag']) {
      $(key+'-tab').setAttribute('aria-selected', String(key===value)); $(key+'-tab').tabIndex = key===value ? 0 : -1;
      $(key+'-panel').hidden = key!==value;
    }
  }
  function render() { renderParty(); renderMon(); renderBag(); refreshStatus(); switchTab(tab); }
  async function load(file) {
    if (!file) return;
    try {
      const next = C.parse(await file.arrayBuffer());
      if (dirty && !confirm('Die Änderungen am aktuellen Spielstand verwerfen und eine andere Datei öffnen?')) return;
      model = next; selected = 0; originalName = file.name; dirty = false; tab = 'team';
      originalState = JSON.stringify({party: model.party, bag: model.bag});
      $('filename').textContent = file.name;
      $('trainer').textContent = `${model.player} · Trainer-ID ${String(model.trainerId).padStart(5,'0')}`;
      $('format').textContent = `Format ${model.format} · ${model.capacity} Beutelplätze`;
      $('drop').hidden = true; $('start-note').hidden = true; $('editor').hidden = false;
      message('Spielstand geladen. Beim Speichern wird eine neue Datei erstellt.'); render();
    } catch (error) { message(error.message, true); }
    $('file').value = '';
  }
  for (const id of ['open','replace']) $(id).addEventListener('click', () => $('file').click());
  $('file').addEventListener('change', e => load(e.target.files[0]));
  for (const event of ['dragenter','dragover']) $('drop').addEventListener(event, e => { e.preventDefault(); $('drop').classList.add('over'); });
  $('drop').addEventListener('dragleave', () => $('drop').classList.remove('over'));
  $('drop').addEventListener('drop', e => { e.preventDefault(); $('drop').classList.remove('over'); load(e.dataTransfer.files[0]); });
  $('reset').addEventListener('click', () => {
    if (!dirty || confirm('Alle Änderungen verwerfen und die ursprüngliche Datei wiederherstellen?')) {
      model = C.parse(model.original); dirty = false; selected = 0; message('Änderungen zurückgesetzt.'); render();
    }
  });
  $('download').addEventListener('click', () => {
    try {
      const bytes = C.exportSave(model);
      const filename = originalName.replace(/\.(sav|ram)$/i, '') + '-bearbeitet.sav';
      const url = URL.createObjectURL(new Blob([bytes], {type:'application/octet-stream'}));
      const anchor = el('a', {href:url,download:filename}); document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
      dirty = false; refreshStatus(); message(`„${filename}“ wurde als Kopie heruntergeladen. Den Emulator schließen, die bearbeitete Datei als Spielstand verwenden und normal laden.`);
    } catch (error) { message(error.message, true); }
  });
  for (const key of ['team','bag']) {
    $(key+'-tab').addEventListener('click', () => switchTab(key));
    $(key+'-tab').addEventListener('keydown', e => { if (['ArrowLeft','ArrowRight','Home','End'].includes(e.key)) { e.preventDefault(); const next = e.key==='Home' ? 'team' : e.key==='End' ? 'bag' : key==='team' ? 'bag' : 'team'; switchTab(next); $(next+'-tab').focus(); } });
  }
  $('add-bag').addEventListener('click', () => {
    const count = Number($('add-count').value), id = Number($('add-item').value);
    if (!Number.isInteger(count) || count < 1 || count > 99) { message('Die Itemmenge muss zwischen 1 und 99 liegen.', true); return; }
    if (model.bag.length >= model.capacity || !C.items.has(id) || model.bag.some(i => i.id === id)) return;
    model.bag.push({id,count}); message(''); mark(); renderBag();
  });
  $('sort-bag').addEventListener('click', () => { model.bag.sort((a,b) => (C.items.get(a.id)?.name || '').localeCompare(C.items.get(b.id)?.name || '', 'de')); mark(); renderBag(); });
  window.addEventListener('beforeunload', e => { if (dirty) { e.preventDefault(); e.returnValue = ''; } });
})();
