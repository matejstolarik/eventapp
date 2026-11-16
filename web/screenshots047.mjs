import { chromium } from '@playwright/test'
import path from 'path'
import { mkdirSync } from 'fs'

const BASE = 'http://localhost:5174/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\047'
mkdirSync(OUT, { recursive: true })

const TODAY = '2026-11-16'
const TOMORROW = '2026-11-17'

const VENUES = [
  { id: 'akropolis', name: 'Palác Akropolis', lat: 50.0787, lng: 14.4592, character: ['alternative'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Kubelíkova 27', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'cross-club', name: 'Cross Club', lat: 50.1082927, lng: 14.4432281, character: ['underground', 'late-night'], type: ['dance-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Plynární 23', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'roxy', name: 'ROXY', lat: 50.0882, lng: 14.4252, character: ['alternative', 'late-night'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Dlouhá 33', city: 'Praha', size: 'large', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'meetfactory', name: 'MeetFactory', lat: 50.0506, lng: 14.4034, character: ['art-space'], type: ['art-space'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Ke Sklárně 15', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'archa', name: 'Archa+', lat: 50.0901, lng: 14.4204, character: ['english-friendly'], type: ['theatre'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Na Poříčí 26', city: 'Praha', size: 'small', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
]

function ev(id, venue_id, title, date, start_time, formats, genres, extra) {
  return {
    id, venue_id, title, date, start_time, end_time: null, doors_time: null,
    formats, genres, character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [{ type: 'rss', url: 'https://example.com' }],
    classification: null, first_seen: TODAY, last_seen: TODAY, status: 'scheduled', flags: [],
    ...extra
  }
}

const EVENTS = [
  ev('ev1', 'akropolis', 'Nová Vlna – krst albumu', TODAY, '20:00', ['concert'], ['indie', 'post-punk'], { first_seen: TODAY }),
  ev('ev2', 'cross-club', 'Lumen all night long', TODAY, '22:00', ['dj'], ['house', 'techno'], { price_text: '10 €' }),
  ev('ev3', 'roxy', 'Párty 2000s', TODAY, '22:00', ['party'], ['pop', 'disco'], {}),
  ev('ev4', 'meetfactory', 'Mesto a my: diskusia', TODAY, '19:00', ['talk'], [], {}),
  ev('ev5', 'archa', 'Hamlet remix', TODAY, '20:00', ['theatre'], [], { sold_out: true }),
  ev('ev6', 'cross-club', 'Bass Shift', TODAY, '23:00', ['dj'], ['drum-and-bass'], {}),
  ev('ev7', 'akropolis', 'Echo Park', TODAY, '20:30', ['concert'], ['indie'], {}),
  ev('ev8', 'roxy', 'Club Mix', TODAY, '23:00', ['party'], ['house', 'techno'], {}),
  ev('ev9', 'meetfactory', 'Open studio', TODAY, '18:00', ['opening'], [], {}),
  ev('ev10', 'akropolis', 'Jazz Night', TOMORROW, '20:00', ['concert'], ['jazz'], {}),
  ev('ev11', 'cross-club', 'Sunday Club', TOMORROW, '22:00', ['party'], ['techno'], {}),
]

const SYNTHETIC = JSON.stringify({ schema_version: 1, generated_at: '2026-11-16T18:00:00', venues: VENUES, events: EVENTS })

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
})

await ctx.addInitScript(() => {
  localStorage.setItem('language', 'sk')
  localStorage.removeItem('eventsPeriod')
  localStorage.removeItem('eventsSort')
  localStorage.removeItem('going')
})

await ctx.route('**/events.json', (route) => {
  route.fulfill({ contentType: 'application/json', body: SYNTHETIC })
})

const page = await ctx.newPage()
function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

async function goEvents() {
  await page.goto(BASE)
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await sleep(1500)
  // Click Events tab (second tab from left in bottom nav)
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'))
    for (const b of btns) {
      const label = b.getAttribute('aria-label')
      if (label === 'Akcie' || label === 'Events') { b.click(); return }
    }
    // fallback: second tab button
    const tabBtns = btns.filter(b => {
      const rect = b.getBoundingClientRect()
      return rect.bottom > 740 && rect.top > 700
    })
    if (tabBtns[1]) tabBtns[1].click()
  })
  await sleep(600)
}

async function openEvent(titleText) {
  await page.evaluate((t) => {
    // Click the first element whose textContent matches
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT)
    let node
    while ((node = walker.nextNode())) {
      if (node.textContent.trim() === t) {
        const el = node.parentElement
        const card = el.closest('a') || el.closest('[role="button"]') || el.closest('[style*="cursor: pointer"]')
        if (card) { card.click(); return }
        el.click(); return
      }
    }
  }, titleText)
  await sleep(600)
}

// --- 01: Events list showing card with type tag ---
await goEvents()
await page.screenshot({ path: path.join(OUT, '01-karta-stitok-typu.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ 01-karta-stitok-typu.jpg')

// --- 02: Event page without price (bookmark on tag row) ---
await openEvent('Nová Vlna – krst albumu')
await sleep(300)
await page.screenshot({ path: path.join(OUT, '02-akcia-bez-ceny.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ 02-akcia-bez-ceny.jpg')

// --- 03: Event page sold out without price ---
await page.evaluate(() => { history.back() })
await sleep(500)
await openEvent('Hamlet remix')
await sleep(300)
await page.screenshot({ path: path.join(OUT, '03-akcia-vypredane-bez-ceny.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ 03-akcia-vypredane-bez-ceny.jpg')

// --- 04: Period selection panel ---
await page.evaluate(() => { history.back() })
await sleep(500)
await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  for (const b of btns) {
    if (b.textContent.includes('Dnes') && b.getBoundingClientRect().height > 0) {
      b.click(); return
    }
  }
})
await sleep(400)
await page.screenshot({ path: path.join(OUT, '04-panel-obdobia.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ 04-panel-obdobia.jpg')

// --- 05: Sort inline menu (switch to 7-day first) ---
// close period panel via Escape
await page.keyboard.press('Escape')
await sleep(300)
// click period to switch to 7 days
await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  for (const b of btns) {
    if (b.textContent.includes('Dnes') && b.getBoundingClientRect().height > 0) {
      b.click(); return
    }
  }
})
await sleep(300)
await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  for (const b of btns) {
    if (b.textContent.includes('7 dní') || b.textContent.includes('7 dn')) { b.click(); return }
  }
})
await sleep(400)
// Click sort button
await page.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  for (const b of btns) {
    const txt = b.textContent || ''
    if (txt.includes('dátum') || txt.includes('Zoradiť') || txt.includes('datum')) {
      b.click(); return
    }
  }
})
await sleep(400)
await page.screenshot({ path: path.join(OUT, '05-zoradenie-ponuka.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ 05-zoradenie-ponuka.jpg')

await browser.close()
console.log('All screenshots done.')
