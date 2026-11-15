// Main-chat review helper (task 034). Usage: start 'npx vite --port 5199' in web/, create a synthetic events.json
// (all venues from data/venues.json with one event today), then: EVENTS_JSON=/path/events.json node scripts/review/map-names-check.js
// The map style is stubbed (no tiles), only pins and names are rendered.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  await p.addInitScript(() => localStorage.setItem('lang', 'sk'));
  await p.route('**/events.json', r => r.fulfill({ path: 'process.env.EVENTS_JSON || 'events.json'', contentType: 'application/json' }));
  await p.route('https://tiles.openfreemap.org/**', r => {
    if (r.request().url().includes('/styles/')) return r.fulfill({ contentType: 'application/json', body: JSON.stringify({ version: 8, sources: { openmaptiles: { type: 'vector', tiles: ['https://tiles.openfreemap.org/none/{z}/{x}/{y}.pbf'], maxzoom: 14 } }, glyphs: 'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf', sprite: 'https://tiles.openfreemap.org/sprites/x', layers: [] }) });
    return r.fulfill({ status: 404, body: '' });
  });
  p.on('console', m => { if (m.type()==='error') console.log('CONSOLE', m.text().slice(0,150)); });
  await p.goto('http://localhost:5199/eventapp/?debugPair=1');
  await p.waitForTimeout(4000);
  const state = () => p.evaluate(() => {
    const out = [];
    document.querySelectorAll('.pin-name').forEach(n => {
      const r = n.getBoundingClientRect(); const cs = getComputedStyle(n);
      if (r.width) out.push(`${n.textContent}${cs.visibility==='hidden'?'(H)':''}@${Math.round(r.left+r.width/2)},${Math.round(r.top)}`);
    });
    let comb = '';
    document.querySelectorAll('.pin-combined-name').forEach(c => { const r=c.getBoundingClientRect(); if (getComputedStyle(c).display!=='none') comb += `[${c.textContent} @${Math.round(r.left+r.width/2)},${Math.round(r.top)}] `; });
    return out.join(' | ') + '\n   COMBINED: ' + comb;
  });
  const findName = (t) => p.evaluate((t) => { for (const n of document.querySelectorAll('.pin-name')) if (n.textContent.toLowerCase().includes(t)) { const r=n.parentElement.getBoundingClientRect(); return [r.left+r.width/2, r.top+r.height/2]; } return null; }, t);
  const zoomAt = async (t, steps) => {
    for (let i=0;i<steps;i++){ const pos = (await findName(t)) || [195,422]; await p.mouse.move(pos[0], pos[1]); await p.mouse.wheel(0,-240); await p.waitForTimeout(400); }
    await p.waitForTimeout(900);
  };
  console.log('start:', await state());
  for (let i=1;i<=12;i++) { await zoomAt('fuchs', 1); console.log('fuchs', i, ':', await state()); if (i===6) await p.screenshot({path:'f6.png'}); if (i===12) await p.screenshot({path:'f12.png'}); }
  await p.mouse.move(195, 500); await p.mouse.down(); await p.mouse.move(150, 450, { steps: 5 });
  console.log('mid-drag:', await state());
  await p.mouse.up(); await p.waitForTimeout(800);
  // zoom out a lot
  for (let i=0;i<10;i++){ await p.mouse.move(195,422); await p.mouse.wheel(0,240); await p.waitForTimeout(300);} await p.waitForTimeout(900);
  console.log('zoomed out:', await state());
  // Roxy/EPIC
  for (let i=1;i<=10;i++) { await zoomAt('roxy', 1); if (i%2===0) console.log('roxy', i, ':', await state()); }
  await p.screenshot({path:'roxy.png'});
  await b.close();
})();
