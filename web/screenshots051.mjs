/**
 * Task 051 screenshots: map pins with new icons, events grid without venue tags.
 * Run from web/ directory: node screenshots051.mjs
 * Dev server must be running on port 5173.
 */
import { chromium } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const BASE = 'http://localhost:5173/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\051'
fs.mkdirSync(OUT, { recursive: true })
const THUMB_DIR = 'D:/AI/eventapp/tests/playwright/fixtures/thumbs'

const FROZEN_ISO = '2026-11-16T18:00:00'
const TODAY = '2026-11-16'

function ev(id, venue_id, title, date, start_time, formats, genres, extra = {}) {
  return {
    id, venue_id, title, date, start_time, end_time: null, doors_time: null,
    formats, genres, character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [{ type: 'rss', url: 'https://example.com' }],
    classification: null, first_seen: TODAY, last_seen: TODAY, status: 'scheduled', flags: [],
    ...extra,
  }
}

const VENUES = [
  { id: 'akropolis',   name: 'Palác Akropolis',     lat: 50.0787, lng: 14.4592, character: ['alternative'],          type: ['concert-club'],  image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: 'palacakropolis', address: 'Kubelíkova 27', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'kino-aero',   name: 'Kino Aero',            lat: 50.0821, lng: 14.4620, character: ['english-friendly'],     type: ['cinema'],        image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null,              address: 'Biskupcova 31', city: 'Praha', size: 'small',  sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'cross-club',  name: 'Cross Club',           lat: 50.1083, lng: 14.4432, character: ['underground'],          type: ['dance-club'],    image_url: null, image_thumb: null, active: true, web: '',                   ra_url: null, instagram: null,              address: 'Plynární 23',   city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'comedy-club', name: 'Comedy Club Praha',    lat: 50.0865, lng: 14.4208, character: [],                       type: ['culture-center'],image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null,              address: 'Revoluční 1',  city: 'Praha', size: 'small',  sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'dance-venue', name: 'Taneční Studio',       lat: 50.0730, lng: 14.4350, character: [],                       type: ['culture-center'],image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null,              address: 'Vinohrady 5',  city: 'Praha', size: 'small',  sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'theatre',     name: 'Divadlo v Řeznické',   lat: 50.0760, lng: 14.4280, character: [],                       type: ['theatre'],       image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null,              address: 'Řeznická 12',  city: 'Praha', size: 'small',  sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'party-club',  name: 'Club Budoár',          lat: 50.0810, lng: 14.4150, character: ['late-night'],           type: ['dance-club'],    image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null,              address: 'Štěpánská 20', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
]

const EVENTS = [
  ev('ev-concert', 'akropolis',   'Live: Nová Vlna',          TODAY, '20:00', ['concert'], ['indie'], { image_thumb: '/eventapp/test-thumb-concert.jpg' }),
  ev('ev-party',   'party-club',  'Párty noc',                TODAY, '22:00', ['party'], ['pop'],     { image_thumb: '/eventapp/test-thumb-party.jpg' }),
  ev('ev-dj',      'cross-club',  'DJ Nights',                TODAY, '23:00', ['dj'], []),
  ev('ev-film',    'kino-aero',   'Filmová premiéra',         TODAY, '19:00', ['film'], ['documentary'], { image_thumb: '/eventapp/test-thumb-film.jpg' }),
  ev('ev-comedy',  'comedy-club', 'Stand-up večer',           TODAY, '20:30', ['comedy'], []),
  ev('ev-dance',   'dance-venue', 'Taneční predstavenie',     TODAY, '19:30', ['dance'], []),
  ev('ev-theatre', 'theatre',     'Hamlet remix',             TODAY, '20:00', ['theatre'], []),
]

const SYNTHETIC = JSON.stringify({ schema_version: 1, generated_at: FROZEN_ISO, venues: VENUES, events: EVENTS })

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
})

await ctx.addInitScript(() => {
  localStorage.setItem('language', 'sk')
  localStorage.removeItem('eventsPeriod')
  localStorage.removeItem('eventsSort')
  localStorage.removeItem('eventsFilters')
})

// Test thumbnails live outside web/public (task 052) so they never reach Pages
await ctx.route('**/test-thumb*.jpg', route => {
  const name = path.basename(new URL(route.request().url()).pathname)
  route.fulfill({ contentType: 'image/jpeg', body: fs.readFileSync(path.join(THUMB_DIR, name)) })
})
await ctx.route('**/events.json', route => {
  route.fulfill({ contentType: 'application/json', body: SYNTHETIC })
})

const page = await ctx.newPage()
await page.clock.setFixedTime(FROZEN_ISO)

// --- mapa-piny ---
await page.goto(BASE)
await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
await page.waitForTimeout(2500)
await page.screenshot({ path: path.join(OUT, 'mapa-piny.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ mapa-piny.jpg')

// --- akcie-mriezka ---
await page.evaluate(() => {
  const buttons = Array.from(document.querySelectorAll('button'))
  const tabBtns = buttons.filter(b => {
    const rect = b.getBoundingClientRect()
    return rect.bottom > 740 && rect.top > 700
  })
  if (tabBtns[1]) tabBtns[1].click()
})
await page.waitForTimeout(800)
await page.screenshot({ path: path.join(OUT, 'akcie-mriezka.jpg'), type: 'jpeg', quality: 80 })
console.log('✓ akcie-mriezka.jpg')

await browser.close()
console.log('Done. Screenshots in', OUT)
