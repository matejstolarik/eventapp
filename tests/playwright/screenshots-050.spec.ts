import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/050')
fs.mkdirSync(OUT_DIR, { recursive: true })

const FROZEN_ISO = '2026-11-16T18:00:00'
const TODAY = '2026-11-16'
const TOMORROW = '2026-11-17'

// Minimal 2x2 blue JPEG for event thumbs (served via route interception)
const THUMB_B64 =
  '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoH' +
  'BwYIDAoMCwsKCwsNCxAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQME' +
  'BAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU' +
  'FBQUFBQUFBT/wAARCAAKAAoDASIAAhEBAxEB/8QAFgABAQEAAAAAAAAAAAAAAAAACAAH' +
  '/8QAJhAAAgIBAwMFAQAAAAAAAAAAAQIDBAUREiExBhNBUWGB/8QAFAEBAAAAAAAAAAAAAAAAAAAAAv/' +
  'EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AMnxWLi8bxuFpYlbJZHI3rFqO' +
  'SxdqV3SRpFiVVjjVQFCqoAA9ACfcnz2Lz9bCbQ2bFfH2k5LNyO3L/AIokkjRh+gLEf0d6' +
  'D4rJi6kVanBHBBGoSKKJAiIo8BQOAAKn1nxelTlBiMk2JsO5cxWiGaVmJLHhZPyHJJP7n' +
  'JoA/9k='

function thumbBuf(): Buffer {
  return Buffer.from(THUMB_B64, 'base64')
}

function ev(
  id: string,
  venue_id: string,
  title: string,
  date: string,
  start_time: string,
  formats: string[],
  genres: string[],
  extra: Partial<{ price_text: string | null; sold_out: boolean; first_seen: string; image_thumb: string | null; image_url: string | null }> = {}
): object {
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
  { id: 'akropolis', name: 'Palác Akropolis', lat: 50.0787, lng: 14.4592, character: ['alternative'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: 'palacakropolis', address: 'Kubelíkova 27', city: 'Praha', size: 'medium', sources: [], description: 'Kultovní pražský klub v Žižkově.', description_url: null, image_source: null, music: [], closing: null },
  { id: 'kino-aero', name: 'Kino Aero', lat: 50.0821, lng: 14.4620, character: ['english-friendly'], type: ['cinema'], image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null, address: 'Biskupcova 31', city: 'Praha', size: 'small', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'cross-club', name: 'Cross Club', lat: 50.1082927, lng: 14.4432281, character: ['underground', 'late-night'], type: ['dance-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Plynární 23', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'archa', name: 'Archa+', lat: 50.0901, lng: 14.4204, character: ['english-friendly'], type: ['theatre'], image_url: null, image_thumb: null, active: true, web: 'https://example.com', ra_url: null, instagram: null, address: 'Na Poříčí 26', city: 'Praha', size: 'small', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
]

const EVENTS = [
  // Concert with genres (has image)
  ev('ev1', 'akropolis', 'Nová Vlna – krst albumu', TODAY, '20:00', ['concert'], ['indie', 'post-punk'], { image_thumb: '/eventapp/test-thumb-concert.jpg', image_url: '/eventapp/test-thumb-concert.jpg' }),
  // DJ no genres fallback (has image)
  ev('ev2', 'cross-club', 'Lumen all night long', TODAY, '22:00', ['dj'], [], { image_thumb: '/eventapp/test-thumb-dj.jpg', price_text: '10 €' }),
  // Party with genres (has image)
  ev('ev3', 'archa', 'Párty 2000s', TODAY, '22:00', ['party'], ['pop', 'disco'], { image_thumb: '/eventapp/test-thumb-party.jpg' }),
  // Culture film with genres (has image)
  ev('ev4', 'kino-aero', 'Nový film premiéra', TODAY, '19:00', ['film'], ['documentary'], { image_thumb: '/eventapp/test-thumb-film.jpg', image_url: '/eventapp/test-thumb-film.jpg' }),
  // Culture talk without genres – fallback: returns ['talk']
  ev('ev5', 'archa', 'Diskusia o meste', TODAY, '18:00', ['talk'], [], {}),
  // Concert for venue programme
  ev('ev6', 'akropolis', 'Jazz Night', TOMORROW, '20:00', ['concert'], ['jazz'], { image_thumb: '/eventapp/test-thumb-concert.jpg' }),
  // Culture theatre without genres – fallback
  ev('ev7', 'akropolis', 'Hamlet remix', TOMORROW, '20:00', ['theatre'], [], {}),
]

const SYNTHETIC = { schema_version: 1, generated_at: FROZEN_ISO, venues: VENUES, events: EVENTS }

async function setup(page: any) {
  await page.clock.setFixedTime(FROZEN_ISO)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.removeItem('eventsPeriod')
    localStorage.removeItem('eventsSort')
    localStorage.removeItem('eventsFilters')
  })
  await page.route('**/events.json', (route: any) => {
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(SYNTHETIC) })
  })
  // Serve test thumbnails as a solid-color JPEG
  await page.route('**/test-thumb*.jpg', (route: any) => {
    route.fulfill({ contentType: 'image/jpeg', body: thumbBuf() })
  })
}

async function goToEvents(page: any) {
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(1500)
  await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
    const tabBtns = buttons.filter(b => {
      const rect = b.getBoundingClientRect()
      return rect.bottom > 740 && rect.top > 700
    })
    if (tabBtns[1]) tabBtns[1].click()
  })
  await page.waitForTimeout(600)
}

test.describe('050', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie-mriezka', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    await page.waitForTimeout(500)
    await page.screenshot({ path: path.join(OUT_DIR, 'akcie-mriezka.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ akcie-mriezka.jpg')
  })

  test('mapa-karta', async ({ page }) => {
    await setup(page)
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2000)
    // Click on the first pin visible on the map canvas
    await page.evaluate(() => {
      const markers = Array.from(document.querySelectorAll('.maplibregl-marker')) as HTMLElement[]
      if (markers[0]) markers[0].click()
    })
    await page.waitForTimeout(800)
    await page.screenshot({ path: path.join(OUT_DIR, 'mapa-karta.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ mapa-karta.jpg')
  })

  test('podnik-program', async ({ page }) => {
    await setup(page)
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(1500)
    // Go to Venues tab (index 2)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      const tabBtns = buttons.filter(b => {
        const rect = b.getBoundingClientRect()
        return rect.bottom > 740 && rect.top > 700
      })
      if (tabBtns[2]) tabBtns[2].click()
    })
    await page.waitForTimeout(500)
    // Click on Palác Akropolis
    await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('*')) as HTMLElement[]
      for (const el of els) {
        if (el.textContent?.trim() === 'Palác Akropolis' && el.offsetHeight > 0 && el.children.length === 0) {
          el.click(); return
        }
      }
    })
    await page.waitForTimeout(600)
    await page.screenshot({ path: path.join(OUT_DIR, 'podnik-program.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ podnik-program.jpg')
  })

  test('stranka-akcie-koncert', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    await page.waitForTimeout(400)
    // Open first event (concert)
    await page.evaluate(() => {
      const cards = Array.from(document.querySelectorAll('[role="button"]')) as HTMLElement[]
      if (cards[0]) cards[0].click()
    })
    await page.waitForTimeout(500)
    await page.screenshot({ path: path.join(OUT_DIR, 'stranka-akcie-koncert.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ stranka-akcie-koncert.jpg')
  })

  test('stranka-akcie-film', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    await page.waitForTimeout(400)
    // Open culture film event (ev4 - 'Nový film premiéra')
    await page.evaluate(() => {
      const cards = Array.from(document.querySelectorAll('[role="button"]')) as HTMLElement[]
      for (const card of cards) {
        if (card.textContent?.includes('Nový film')) { card.click(); return }
      }
    })
    await page.waitForTimeout(500)
    await page.screenshot({ path: path.join(OUT_DIR, 'stranka-akcie-film.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ stranka-akcie-film.jpg')
  })
})
