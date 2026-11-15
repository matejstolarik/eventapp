/**
 * Task 035 screenshots – night mode, stale pins, pulse.
 * Run from web/ with a vite dev server on port 5173:
 *   npm run dev &
 *   node screenshots035.mjs
 */
import { chromium } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const BASE = 'http://localhost:5173/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\035'
fs.mkdirSync(OUT, { recursive: true })

// Clock frozen at Saturday 2026-11-21 01:30 (Prague local)
// getToday(now) returns 2026-11-20 (Fri) because hour < 5
const FROZEN_MS = new Date('2026-11-21T01:30:00').getTime()
const PREV_DAY  = '2026-11-20'  // Friday night events
const CAL_TODAY = '2026-11-21'  // Calendar today (Saturday)
const DAY3      = '2026-11-24'  // 3 days from calendar Saturday

const SYNTHETIC_EVENTS = {
  generated_at: '2026-11-21T01:00:00',
  venues: [
    { id: 'cross-club',     name: 'Cross Club',      lat: 50.1082927, lng: 14.4432281,
      character: ['alternative','underground','late-night'], type: ['concert-club','dance-club'] },
    { id: 'fuchs2',         name: 'Fuchs2',           lat: 50.0902,    lng: 14.4214,
      character: ['underground','queer-friendly','late-night'], type: ['dance-club'] },
    { id: 'roxy',           name: 'ROXY',             lat: 50.0882,    lng: 14.4252,
      character: ['alternative','late-night'], type: ['concert-club','dance-club'] },
    { id: 'epic',           name: 'EPIC Prague',      lat: 50.0803,    lng: 14.4196,
      character: ['commercial','student','late-night'], type: ['dance-club'] },
    { id: 'kasarna-karlin', name: 'Kasárna Karlín',   lat: 50.0920,    lng: 14.4610,
      character: ['alternative','hangout','community'], type: ['cultural-center'] },
    { id: 'forum-karlin',   name: 'Forum Karlín',     lat: 50.0896,    lng: 14.4548,
      character: ['commercial'], type: ['concert-hall'] }
  ],
  events: [
    // Friday night – party/dj → show in NIGHT_DAY + pulse at 01:30
    { id: 'ev-cc-party',   venue_id: 'cross-club',     title: 'Techno párty',
      date: PREV_DAY, start_time: '23:00', end_time: null,
      formats: ['party'], genres: ['techno'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://crossclub.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    { id: 'ev-f2-dj',     venue_id: 'fuchs2',          title: 'DJ Night',
      date: PREV_DAY, start_time: '23:00', end_time: null,
      formats: ['dj'], genres: ['house'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://fuchs2.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    { id: 'ev-roxy-dj',   venue_id: 'roxy',            title: 'ROXY late night',
      date: PREV_DAY, start_time: '22:00', end_time: null,
      formats: ['dj'], genres: ['house'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://roxy.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    // Friday concert without end – should NOT appear in night mode
    { id: 'ev-kasarna-concert', venue_id: 'kasarna-karlin', title: 'Večerný koncert',
      date: PREV_DAY, start_time: '20:00', end_time: null,
      formats: ['concert'], genres: ['indie'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://kasarna.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    // Calendar today (Sat Nov 21) – for the day list
    { id: 'ev-kasarna-today', venue_id: 'kasarna-karlin', title: 'Sobotný program',
      date: CAL_TODAY, start_time: '18:00', end_time: '22:00',
      formats: ['concert'], genres: ['folk'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://kasarna.cz' }],
      classification: null, first_seen: CAL_TODAY, last_seen: CAL_TODAY,
      status: 'scheduled', flags: [] },
    // Day+3 (Tue Nov 24) – for screenshot 04, should not pulse
    { id: 'ev-epic-day3',  venue_id: 'epic',            title: 'EPIC Friday',
      date: DAY3, start_time: '22:00', end_time: '05:00',
      formats: ['party'], genres: ['commercial'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://epic.cz' }],
      classification: null, first_seen: DAY3, last_seen: DAY3,
      status: 'scheduled', flags: [] },
    { id: 'ev-forum-day3', venue_id: 'forum-karlin',    title: 'Forum concert',
      date: DAY3, start_time: '20:00', end_time: '23:00',
      formats: ['concert'], genres: ['pop'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://forum.cz' }],
      classification: null, first_seen: DAY3, last_seen: DAY3,
      status: 'scheduled', flags: [] }
  ]
}

async function newPage(browser, extraInit) {
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })
  if (extraInit) await ctx.addInitScript(extraInit)
  await ctx.addInitScript(() => { localStorage.setItem('language', 'sk') })
  const page = await ctx.newPage()
  await page.clock.setFixedTime(FROZEN_MS)
  await page.route('**/events.json', route =>
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(SYNTHETIC_EVENTS) })
  )
  return { page, ctx }
}

async function waitForMap(page) {
  await page.goto(BASE)
  await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
  await page.waitForTimeout(2500)
}

async function jpeg(page, name) {
  await page.screenshot({ path: path.join(OUT, `${name}.jpg`), type: 'jpeg', quality: 80 })
  console.log(`✓ ${name}.jpg`)
}

const browser = await chromium.launch({ headless: true })

// 01 – map at startup at 01:30 → auto-selects NIGHT_DAY
{
  const { page, ctx } = await newPage(browser)
  await waitForMap(page)
  await jpeg(page, '01-noc-predvolene')
  await ctx.close()
}

// 02 – open day selector in night mode
{
  const { page, ctx } = await newPage(browser)
  await waitForMap(page)
  // Click the day button (top-left of top bar)
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'))
    for (const b of buttons) {
      const rect = b.getBoundingClientRect()
      if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.left < 220) {
        b.click()
        return
      }
    }
  })
  await page.waitForTimeout(500)
  await jpeg(page, '02-noc-dni')
  await ctx.close()
}

// 03 – night mode + favorites (only cross-club)
{
  const { page, ctx } = await newPage(browser, () => {
    localStorage.setItem('favorites', JSON.stringify(['cross-club']))
  })
  await waitForMap(page)
  // Toggle favorites: find the heart button (top-right of top bar)
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'))
    // Favorites button is on the right side of the top bar
    for (const b of buttons) {
      const rect = b.getBoundingClientRect()
      if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.right > 300) {
        b.click()
        return
      }
    }
  })
  await page.waitForTimeout(700)
  await jpeg(page, '03-noc-oblubene')
  await ctx.close()
}

// 04 – day+3 (Tue Nov 24), no pulse ring on pins
{
  const { page, ctx } = await newPage(browser)
  await waitForMap(page)
  // Open day selector
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button'))
    for (const b of buttons) {
      const rect = b.getBoundingClientRect()
      if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.left < 220) {
        b.click()
        return
      }
    }
  })
  await page.waitForTimeout(400)
  // Click last day button in the bottom sheet (day+3 = index 4: night, Sat, Sun, Mon, Tue)
  await page.evaluate(() => {
    const allBtns = Array.from(document.querySelectorAll('button'))
    const sheetBtns = allBtns.filter(b => {
      const r = b.getBoundingClientRect()
      return r.width > 200 && r.top > 200
    })
    // 0=V noci, 1=Dnes(Sat Nov21), 2=Zajtra(Sun Nov22), 3=Mon Nov23, 4=Tue Nov24
    const target = sheetBtns[4] || sheetBtns[sheetBtns.length - 1]
    if (target) target.click()
  })
  await page.waitForTimeout(1200)
  await jpeg(page, '04-den-o-3-dni')
  await ctx.close()
}

await browser.close()
console.log('Done. Screenshots in', OUT)
