import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/035')
fs.mkdirSync(OUT_DIR, { recursive: true })

// Clock frozen at Saturday 2026-11-21 01:30 Prague local time
// getToday(now) = 2026-11-20 (Fri), since hour < 5
const FROZEN_ISO = '2026-11-21T01:30:00'
const PREV_DAY = '2026-11-20'  // Friday night events
const CAL_TODAY = '2026-11-21' // Calendar today (Saturday)
const DAY3 = '2026-11-24'      // 3 days from Saturday

const SYNTHETIC_EVENTS = {
  generated_at: '2026-11-21T01:00:00',
  venues: [
    { id: 'cross-club',   name: 'Cross Club',      lat: 50.1082927, lng: 14.4432281,
      character: ['alternative','underground','late-night'], type: ['dance-club'] },
    { id: 'fuchs2',       name: 'Fuchs2',           lat: 50.0902,   lng: 14.4214,
      character: ['underground','queer-friendly','late-night'], type: ['dance-club'] },
    { id: 'roxy',         name: 'ROXY',             lat: 50.0882,   lng: 14.4252,
      character: ['alternative','late-night'], type: ['concert-club','dance-club'] },
    { id: 'epic',         name: 'EPIC Prague',      lat: 50.0803,   lng: 14.4196,
      character: ['commercial','student','late-night'], type: ['dance-club'] },
    { id: 'kasarna-karlin', name: 'Kasárna Karlín', lat: 50.0920,   lng: 14.4610,
      character: ['alternative','hangout'], type: ['cultural-center'] },
    { id: 'forum-karlin', name: 'Forum Karlín',     lat: 50.0896,   lng: 14.4548,
      character: ['commercial'], type: ['concert-hall'] }
  ],
  events: [
    // Night events (Fri Nov 20) – should appear in NIGHT_DAY mode
    { id: 'ev-cc-party',  venue_id: 'cross-club',   title: 'Techno párty',
      date: PREV_DAY, start_time: '23:00', end_time: null,
      formats: ['party'], genres: ['techno'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://crossclub.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    { id: 'ev-f2-dj',    venue_id: 'fuchs2',         title: 'DJ Night Fuchs2',
      date: PREV_DAY, start_time: '23:00', end_time: null,
      formats: ['dj'], genres: ['house'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://fuchs2.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    { id: 'ev-roxy-dj',  venue_id: 'roxy',           title: 'ROXY late night',
      date: PREV_DAY, start_time: '22:00', end_time: null,
      formats: ['dj'], genres: ['house'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://roxy.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    // Concert on Fri evening – should NOT appear in night mode (no end, not party/dj, not late-night enough)
    { id: 'ev-kasarna-concert', venue_id: 'kasarna-karlin', title: 'Večerný koncert',
      date: PREV_DAY, start_time: '20:00', end_time: null,
      formats: ['concert'], genres: ['indie'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://kasarna.cz' }],
      classification: null, first_seen: PREV_DAY, last_seen: PREV_DAY,
      status: 'scheduled', flags: [] },
    // Day 3 events (Tue Nov 24) – for screenshot 04, should not pulse
    { id: 'ev-epic-day3', venue_id: 'epic',           title: 'EPIC Saturday',
      date: DAY3, start_time: '22:00', end_time: '05:00',
      formats: ['party'], genres: ['commercial'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://epic.cz' }],
      classification: null, first_seen: DAY3, last_seen: DAY3,
      status: 'scheduled', flags: [] },
    { id: 'ev-forum-day3', venue_id: 'forum-karlin',  title: 'Forum concert',
      date: DAY3, start_time: '20:00', end_time: '23:00',
      formats: ['concert'], genres: ['pop'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://forum.cz' }],
      classification: null, first_seen: DAY3, last_seen: DAY3,
      status: 'scheduled', flags: [] },
    // Day events on calendar today (Sat Nov 21) for the day list
    { id: 'ev-kasarna-today', venue_id: 'kasarna-karlin', title: 'Sobotný program',
      date: CAL_TODAY, start_time: '18:00', end_time: '22:00',
      formats: ['concert'], genres: ['folk'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://kasarna.cz' }],
      classification: null, first_seen: CAL_TODAY, last_seen: CAL_TODAY,
      status: 'scheduled', flags: [] }
  ]
}

async function setupPage(page: any) {
  // Freeze clock
  await page.clock.setFixedTime(FROZEN_ISO)
  // Inject language
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
  })
  // Route events.json
  await page.route('**/events.json', (route: any) => {
    route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify(SYNTHETIC_EVENTS)
    })
  })
}

async function waitForMap(page: any) {
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(2000)
}

async function jpeg(page: any, name: string) {
  await page.screenshot({
    path: path.join(OUT_DIR, `${name}.jpg`),
    type: 'jpeg',
    quality: 80
  })
  console.log(`✓ ${name}.jpg`)
}

test.describe('035 night mode screenshots', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  // 01: map at startup at 01:30 → auto-selects NIGHT_DAY
  test('01-noc-predvolene', async ({ page }) => {
    await setupPage(page)
    await waitForMap(page)
    await jpeg(page, '01-noc-predvolene')
  })

  // 02: open day selector in night mode
  test('02-noc-dni', async ({ page }) => {
    await setupPage(page)
    await waitForMap(page)
    // Click the day button (top bar, leftish)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
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
  })

  // 03: night mode + favorites only
  test('03-noc-oblubene', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('language', 'sk')
      // Favorite cross-club only
      localStorage.setItem('favorites', JSON.stringify(['cross-club']))
    })
    await page.clock.setFixedTime(FROZEN_ISO)
    await page.route('**/events.json', (route: any) => {
      route.fulfill({ contentType: 'application/json', body: JSON.stringify(SYNTHETIC_EVENTS) })
    })
    await waitForMap(page)
    // Toggle favorites: find the heart/star button in top bar
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        const rect = b.getBoundingClientRect()
        if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.right > 300) {
          b.click()
          return
        }
      }
    })
    await page.waitForTimeout(600)
    await jpeg(page, '03-noc-oblubene')
  })

  // 04: day 3 (Tue Nov 24) – no pulse ring on pins
  test('04-den-o-3-dni', async ({ page }) => {
    await setupPage(page)
    await waitForMap(page)
    // Open day selector
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        const rect = b.getBoundingClientRect()
        if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.left < 220) {
          b.click()
          return
        }
      }
    })
    await page.waitForTimeout(400)
    // Click 4th button in the bottom sheet (index 3 = day+3)
    await page.evaluate(() => {
      const allBtns = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      const sheetBtns = allBtns.filter(b => {
        const r = b.getBoundingClientRect()
        return r.width > 200 && r.top > 200
      })
      // Index 0=night, 1=today(Sat), 2=tomorrow, 3=day+2, 4=day+3
      if (sheetBtns[4]) sheetBtns[4].click()
      else if (sheetBtns[sheetBtns.length - 1]) sheetBtns[sheetBtns.length - 1].click()
    })
    await page.waitForTimeout(800)
    await jpeg(page, '04-den-o-3-dni')
  })
})
