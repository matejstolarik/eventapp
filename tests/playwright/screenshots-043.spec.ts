import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/043')
fs.mkdirSync(OUT_DIR, { recursive: true })

// Sunday 2026-11-15 01:00 — night window, yesterday = Saturday 2026-11-14
const SUN_NIGHT = '2026-11-15T01:00:00'
// Monday 2026-11-16 01:00 — night window, yesterday = Sunday 2026-11-15, no events
const MON_NIGHT = '2026-11-16T01:00:00'

const SAT = '2026-11-14'  // Saturday – night events date for SUN_NIGHT scenario
const SUN = '2026-11-15'  // Sunday  – today in SUN_NIGHT scenario

function makeVenue(id: string, name: string, lat: number, lng: number, character: string[], closing: Record<string, string> | null = null): object {
  return {
    id, name, lat, lng, city: 'Praha', address: 'Test', web: '', ra_url: null,
    instagram: null, type: ['dance-club'], character, music: [], size: 'medium',
    description: null, description_url: null, image_url: null, image_source: null,
    image_thumb: null, closing, sources: [], active: true,
  }
}

function makeEvent(id: string, venue_id: string, title: string, date: string, start_time: string, formats: string[], status = 'scheduled'): object {
  return {
    id, venue_id, title, date, start_time, end_time: null, doors_time: null,
    formats, genres: [], character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [{ type: 'rss', url: 'https://example.com' }],
    classification: null, first_seen: SAT, last_seen: SAT, status, flags: [],
  }
}

const VENUES_NIGHT = [
  makeVenue('cross-club', 'Cross Club', 50.1083, 14.4432, ['underground', 'late-night'],
    { mon: '04:00', tue: '05:00', wed: '05:00', thu: '05:00', fri: '05:00', sat: '07:00', sun: '07:00' }),
  makeVenue('roxy', 'ROXY', 50.0882, 14.4252, ['alternative', 'late-night'],
    { mon: '05:00', tue: '22:00', wed: '22:00', thu: '22:00', fri: '05:00', sat: '05:00' }),
  makeVenue('akropolis', 'Palác Akropolis', 50.0787, 14.4592, ['alternative'], null),
]

// Saturday night events (for SUN 01:00 scenario)
const EVENTS_NIGHT = [
  makeEvent('e1', 'cross-club', 'Lumen All Night', SAT, '23:00', ['dj', 'party']),
  makeEvent('e2', 'roxy', 'Club Night', SAT, '22:00', ['party']),
  makeEvent('e3', 'akropolis', 'Jazz Session', SAT, '20:00', ['concert']), // not night event
  // Sunday day events
  makeEvent('e4', 'akropolis', 'Sunday Brunch Jazz', SUN, '12:00', ['concert']),
]

const SYNTHETIC_NIGHT = { schema_version: 1, generated_at: SUN_NIGHT, venues: VENUES_NIGHT, events: EVENTS_NIGHT }
// No night events for Monday scenario
const SYNTHETIC_NO_NIGHT = { schema_version: 1, generated_at: MON_NIGHT, venues: VENUES_NIGHT, events: [
  makeEvent('e4', 'akropolis', 'Monday Talk', '2026-11-16', '19:00', ['concert']),
] }

async function setup(page: any, frozen: string, events: object) {
  await page.clock.setFixedTime(frozen)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.removeItem('eventsPeriod')
    localStorage.removeItem('going')
  })
  await page.route('**/events.json', (route: any) => {
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(events) })
  })
}

async function openDaySelector(page: any) {
  // Click the day selector button (shows current day label)
  const btn = page.locator('[data-testid="day-selector-btn"]')
  if (await btn.count() > 0) {
    await btn.click()
  } else {
    // Fallback: find button by text
    await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      const dayBtn = btns.find(b => ['Dnes', 'V noci', 'Teraz v noci'].includes(b.textContent?.trim() ?? ''))
      dayBtn?.click()
    })
  }
  await page.waitForTimeout(500)
}

async function goToEvents(page: any) {
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
    const tabBtns = buttons.filter(b => {
      const rect = b.getBoundingClientRect()
      return rect.bottom > 740 && rect.top > 700
    })
    if (tabBtns[1]) tabBtns[1].click()
  })
  await page.waitForTimeout(800)
}

async function goToAccount(page: any) {
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
    const tabBtns = buttons.filter(b => {
      const rect = b.getBoundingClientRect()
      return rect.bottom > 740 && rect.top > 700
    })
    if (tabBtns[3]) tabBtns[3].click()
  })
  await page.waitForTimeout(600)
}

test('01-mapa-teraz-v-noci', async ({ page }) => {
  await setup(page, SUN_NIGHT, SYNTHETIC_NIGHT)
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(2000)
  await openDaySelector(page)
  await page.screenshot({
    path: path.join(OUT_DIR, '01-mapa-teraz-v-noci.jpg'),
    clip: { x: 0, y: 0, width: 390, height: 844 },
  })
})

test('02-akcie-v-noci', async ({ page }) => {
  await setup(page, SUN_NIGHT, SYNTHETIC_NIGHT)
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(1500)
  await goToEvents(page)
  await page.screenshot({
    path: path.join(OUT_DIR, '02-akcie-v-noci.jpg'),
    clip: { x: 0, y: 0, width: 390, height: 844 },
  })
})

test('03-akcie-pondelok-1h-nic', async ({ page }) => {
  await setup(page, MON_NIGHT, SYNTHETIC_NO_NIGHT)
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(1500)
  await goToEvents(page)
  await page.screenshot({
    path: path.join(OUT_DIR, '03-akcie-pondelok-1h-nic.jpg'),
    clip: { x: 0, y: 0, width: 390, height: 844 },
  })
})

test('04-jdu', async ({ page }) => {
  await setup(page, SUN_NIGHT, SYNTHETIC_NIGHT)
  await page.addInitScript(() => {
    // Pre-set some going events
    localStorage.setItem('going', JSON.stringify(['e1', 'e4']))
  })
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(1500)
  await goToAccount(page)
  await page.screenshot({
    path: path.join(OUT_DIR, '04-jdu.jpg'),
    clip: { x: 0, y: 0, width: 390, height: 844 },
  })
})
