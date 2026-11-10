import { test } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/029');

fs.mkdirSync(OUT_DIR, { recursive: true });

function delay(ms: number) {
  return new Promise(r => setTimeout(r, ms));
}

async function goToMap(page: any, lang = 'sk') {
  // App reads language from localStorage (detectLanguage in store.ts)
  await page.addInitScript((l: string) => {
    localStorage.setItem('language', l);
  }, lang);
  await page.goto('/eventapp/');
  await delay(2500);
}

async function openDaySelector(page: any) {
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
    // Day button is in top bar, narrow, on the left
    for (const b of buttons) {
      const rect = b.getBoundingClientRect();
      if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.left < 200) {
        b.click();
        return;
      }
    }
  });
  await delay(600);
}

async function clickFutureDay(page: any, index = 1) {
  await page.evaluate((idx: number) => {
    const allBtns = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
    // Sheet buttons are full-width, in the lower half of screen
    const sheetBtns = allBtns.filter(b => {
      const r = b.getBoundingClientRect();
      return r.width > 200 && r.top > 200;
    });
    if (sheetBtns.length > idx) sheetBtns[idx].click();
    else if (sheetBtns.length > 0) sheetBtns[0].click();
  }, index);
  await delay(600);
}

// ── 1. Day selector on 390×844
test('01 day-selector 390x844', async ({ browser }) => {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await goToMap(page, 'sk');
  await openDaySelector(page);
  await page.screenshot({ path: path.join(OUT_DIR, '01-day-selector-390.png') });
  console.log('✓ 01-day-selector-390.png');
  await ctx.close();
});

// ── 2. Day selector on 360×740
test('02 day-selector 360x740', async ({ browser }) => {
  const ctx = await browser.newContext({ viewport: { width: 360, height: 740 } });
  const page = await ctx.newPage();
  await goToMap(page, 'sk');
  await openDaySelector(page);
  await page.screenshot({ path: path.join(OUT_DIR, '02-day-selector-360.png') });
  console.log('✓ 02-day-selector-360.png');
  await ctx.close();
});

// ── 3. Calendar view 390×844
test('03 calendar 390x844', async ({ browser }) => {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await goToMap(page, 'sk');
  await openDaySelector(page);
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
    for (const b of buttons) {
      const text = b.textContent || '';
      if (text.includes('›') || text.includes('Iný') || text.includes('Other')) {
        b.click();
        return;
      }
    }
  });
  await delay(400);
  await page.screenshot({ path: path.join(OUT_DIR, '03-calendar-390.png') });
  console.log('✓ 03-calendar-390.png');
  await ctx.close();
});

// ── 4-9. Top bar in 3 languages, 2 viewports
for (const lang of ['sk', 'cs', 'en']) {
  for (const [w, h] of [[390, 844], [360, 740]] as [number, number][]) {
    test(`topbar ${lang} ${w}`, async ({ browser }) => {
      const ctx = await browser.newContext({ viewport: { width: w, height: h } });
      const page = await ctx.newPage();
      await goToMap(page, lang);
      await page.screenshot({ path: path.join(OUT_DIR, `04-topbar-dnes-${lang}-${w}.png`) });
      console.log(`✓ 04-topbar-dnes-${lang}-${w}.png`);

      await openDaySelector(page);
      await clickFutureDay(page, 1);
      await page.screenshot({ path: path.join(OUT_DIR, `05-topbar-future-${lang}-${w}.png`) });
      console.log(`✓ 05-topbar-future-${lang}-${w}.png`);
      await ctx.close();
    });
  }
}

// ── 10-11. Pin overlap at two zoom levels
test('10-11 pin-overlap zoom levels', async ({ browser }) => {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await goToMap(page, 'sk');
  // Select Nov 12 via calendar
  await openDaySelector(page);
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
    for (const b of buttons) {
      const text = b.textContent || '';
      if (text.includes('›') || text.includes('Iný') || text.includes('Other')) {
        b.click();
        return;
      }
    }
  });
  await delay(400);
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
    for (const b of buttons) {
      if (b.textContent?.trim() === '12') {
        b.click();
        return;
      }
    }
  });
  await delay(600);

  // Zoom in by scrolling on the map canvas (center of viewport) + drag NE toward Štvanica
  // The map starts centered on Prague. Štvanica is NE of center.
  // Scroll up = zoom in; then drag map so Štvanica area comes into view.
  await page.mouse.move(195, 400);
  for (let i = 0; i < 5; i++) {
    await page.mouse.wheel(0, -120); // zoom in
    await delay(200);
  }
  await delay(1000);
  // Drag map slightly right+up to find Holešovice/Štvanica area
  await page.mouse.move(195, 400);
  await page.mouse.down();
  await page.mouse.move(100, 460, { steps: 10 }); // pan right+down (map moves NE)
  await page.mouse.up();
  await delay(1500);
  await page.screenshot({ path: path.join(OUT_DIR, '10-pins-zoom15-390.png') });
  console.log('✓ 10-pins-zoom15-390.png');

  // Zoom out 2 levels
  await page.mouse.move(195, 400);
  for (let i = 0; i < 3; i++) {
    await page.mouse.wheel(0, 120); // zoom out
    await delay(200);
  }
  await delay(1000);
  await page.screenshot({ path: path.join(OUT_DIR, '11-pins-zoom14-390.png') });
  console.log('✓ 11-pins-zoom14-390.png');
  await ctx.close();
});

// ── 12-14. Card preservation: open → event page → back → card still open
test('12-14 card-preservation', async ({ browser }) => {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await goToMap(page, 'sk');

  // Click first pin marker
  const clicked = await page.evaluate(() => {
    const markers = Array.from(document.querySelectorAll('.maplibregl-marker')) as HTMLElement[];
    if (markers.length > 0) { markers[0].click(); return markers.length; }
    return 0;
  });
  await delay(1000);
  await page.screenshot({ path: path.join(OUT_DIR, '12-card-open.png') });
  console.log(`✓ 12-card-open.png (markers: ${clicked})`);

  // Click "Otvoriť akciu" button inside the card to open event page
  const cardEl = await page.evaluate(() => {
    const btn = document.querySelector('button[aria-label="Otvoriť akciu"]') as HTMLButtonElement | null;
    if (btn) { btn.click(); return 'aria-otvoriť'; }
    // Fallback: click in the card area (title zone, y~680)
    const el = document.elementFromPoint(195, 680) as HTMLElement | null;
    if (el) { el.click(); return el.tagName + ':' + el.textContent?.slice(0, 20); }
    return 'nothing';
  });
  await delay(1000);
  await page.screenshot({ path: path.join(OUT_DIR, '13-event-page.png') });
  console.log(`✓ 13-event-page.png (clicked: ${cardEl})`);

  // Go back (same as EventPage's goBack button)
  await page.evaluate(() => window.history.back());
  await delay(1200);
  await page.screenshot({ path: path.join(OUT_DIR, '14-card-after-back.png') });
  console.log('✓ 14-card-after-back.png');
  await ctx.close();
});
