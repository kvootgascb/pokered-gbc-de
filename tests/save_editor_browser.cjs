/* Run codec tests first, then: node tests/save_editor_browser.cjs
   Requires Playwright and Chromium. Tests serve the single offline HTML locally. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const {chromium}=require('playwright');
const html=fs.readFileSync(path.join(__dirname,'../tools/save-editor/Pokemon-DX-Saveeditor.html'));
const data=JSON.parse(html.toString().match(/globalThis.DX_DATA = (.*);\n/)[1]);
const C=require('../tools/save-editor/core.js')(data);
const dir='/tmp/dx-editor-tests';
(async()=>{
  const server=http.createServer((req,res)=>{res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  let browser;
  try {
    browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
    const page=await browser.newPage({viewport:{width:1280,height:1000},acceptDownloads:true});
    const errors=[],external=[];
    page.on('pageerror',e=>errors.push(e.message));
    page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:')&&!r.url().startsWith('data:')&&!r.url().startsWith('blob:'))external.push(r.url());});
    await page.goto('http://127.0.0.1:'+server.address().port);
    await page.locator('#file').setInputFiles(path.join(dir,'original.sav'));
    await page.locator('#editor').waitFor({state:'visible'});
    assert.equal(await page.locator('#download').isDisabled(),false);
    async function download(name){const waiting=page.waitForEvent('download');await page.locator('#download').click();const d=await waiting;assert.match(d.suggestedFilename(),/-bearbeitet\.sav$/);await d.saveAs(path.join(dir,name));return new Uint8Array(fs.readFileSync(path.join(dir,name)));}
    assert.deepEqual(await download('browser-noop.sav'),new Uint8Array(fs.readFileSync(path.join(dir,'original.sav'))));
    await page.getByLabel('Pokémon-Art',{exact:true}).selectOption('21');
    await page.getByLabel('Level',{exact:true}).fill('42');await page.getByLabel('Level',{exact:true}).press('Tab');
    await page.getByLabel('Spitzname',{exact:true}).fill('MÜNCHEN');
    await page.getByLabel('Attacke 1',{exact:true}).selectOption('57');
    await page.getByLabel('AP-Plus Attacke 1',{exact:true}).selectOption('3');
    await page.getByRole('button',{name:'Heilen & AP auffüllen',exact:true}).click();
    for(let i=0;i<5;i++)await page.getByRole('button',{name:'+ Pokémon hinzufügen',exact:true}).click();
    assert.equal(await page.getByRole('button',{name:'+ Pokémon hinzufügen',exact:true}).isDisabled(),true);
    await page.locator('.mon-card').first().click();
    await page.getByRole('button',{name:'Pokémon nach unten',exact:true}).click();
    await page.getByRole('button',{name:'Pokémon nach oben',exact:true}).click();
    await page.screenshot({path:path.join(dir,'browser-team.png'),fullPage:true});
    await page.getByRole('tab',{name:/Beutel/}).click();
    await page.getByLabel('Neues Item',{exact:true}).selectOption('40');await page.getByLabel('Neue Itemmenge',{exact:true}).fill('99');await page.locator('#add-bag').click();
    while(await page.locator('.bag-row').count()<30){const id=await page.locator('#add-item').inputValue();await page.locator('#add-item').selectOption(id);await page.getByLabel('Neue Itemmenge',{exact:true}).fill('1');await page.locator('#add-bag').click();}
    assert.equal(await page.locator('#add-bag').isDisabled(),true);
    await page.getByLabel('Menge Beutelplatz 1',{exact:true}).fill('100');await page.getByLabel('Menge Beutelplatz 1',{exact:true}).press('Tab');
    assert.equal(await page.locator('#download').isDisabled(),true);
    await page.getByLabel('Menge Beutelplatz 1',{exact:true}).fill('99');await page.getByLabel('Menge Beutelplatz 1',{exact:true}).press('Tab');
    assert.equal(await page.locator('#download').isDisabled(),false);
    await page.screenshot({path:path.join(dir,'browser-bag.png'),fullPage:true});
    const output=await download('browser-edited.sav'), m=C.parse(output);
    assert.equal(m.party.length,6);assert.equal(m.party[0].species,21);assert.equal(m.party[0].level,42);assert.equal(m.party[0].nickname,'MÜNCHEN');
    assert.deepEqual(m.party[0].moves[0],{id:57,pp:24,ups:3});assert.equal(m.bag.length,30);assert.deepEqual(m.bag[0],{id:40,count:99});
    assert.equal(m.party[0].hp,C.stats(m.party[0])[0]);
    await page.setViewportSize({width:390,height:844});
    await page.getByRole('tab',{name:/Team/}).click();
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),'mobile overflow');
    await page.screenshot({path:path.join(dir,'browser-mobile.png'),fullPage:true});
    await page.getByRole('tab',{name:/Team/}).focus();await page.keyboard.press('ArrowRight');
    assert.equal(await page.getByRole('tab',{name:/Beutel/}).getAttribute('aria-selected'),'true');
    await page.locator('#reset').click();
    assert.equal(await page.locator('.mon-card').count(),1);assert.equal(await page.locator('.bag-row').count(),0);
    const bad=fs.readFileSync(path.join(dir,'original.sav'));bad[0x2600]^=1;
    await page.locator('#file').setInputFiles({name:'kaputt.sav',mimeType:'application/octet-stream',buffer:bad});
    await page.waitForFunction(()=>document.getElementById('message').textContent.includes('Prüfsumme'));
    assert.equal(await page.locator('#filename').textContent(),'original.sav');
    assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
    console.log('PASS: browser import/no-op, party/moves/PP/level/nickname edits, six slots, 30 items, validation, download, reset, mobile, keyboard and zero external requests');
  } finally {if(browser)await browser.close();await new Promise(r=>server.close(r));}
})().catch(e=>{console.error(e);process.exitCode=1;});
