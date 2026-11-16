import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/047')
fs.mkdirSync(OUT_DIR, { recursive: true })

const FROZEN_ISO = '2026-11-16T18:00:00'
const TODAY = '2026-11-16'
const TOMORROW = '2026-11-17'

const VENUES = [
  { id: 'akropolis', name: 'Palác Akropolis', lat: 50.0787, lng: 14.4592, character: ['alternative'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Kubelíkova 27', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'cross-club', name: 'Cross Club', lat: 50.1082927, lng: 14.4432281, character: ['underground', 'late-night'], type: ['dance-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Plynární 23', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'roxy', name: 'ROXY', lat: 50.0882, lng: 14.4252, character: ['alternative', 'late-night'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Dlouhá 33', city: 'Praha', size: 'large', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'meetfactory', name: 'MeetFactory', lat: 50.0506, lng: 14.4034, character: ['art-space'], type: ['art-space'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Ke Sklárně 15', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
  { id: 'archa', name: 'Archa+', lat: 50.0901, lng: 14.4204, character: ['english-friendly'], type: ['theatre'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Na Poříčí 26', city: 'Praha', size: 'small', sources: [], description: null, description_url: null, image_source: null, music: [], closing: null },
]

function ev(id: string, venue_id: string, title: string, date: string, start_time: string, formats: string[], genres: string[], extra: Partial<{ price_text: string | null, sold_out: boolean, first_seen: string }>): object {
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
  ev('ev1', 'akropolis', 'Nová Vlna – krst albumu', TODAY, '20:00', ['concert'], ['indie', 'post-punk'], {}),
  ev('ev2', 'cross-club', 'Lumen all night long', TODAY, '22:00', ['dj'], ['house', 'techno'], { price_text: '10 €' }),
  ev('ev3', 'roxy', 'Párty 2000s', TODAY, '22:00', ['party'], ['pop', 'disco'], {}),
  ev('ev4', 'meetfactory', 'Mesto a my: diskusia', TODAY, '19:00', ['talk'], [], {}),
  ev('ev5', 'archa', 'Hamlet remix', TODAY, '20:00', ['theatre'], [], { sold_out: true }),
  ev('ev6', 'cross-club', 'Bass Shift', TODAY, '23:00', ['dj'], ['drum-and-bass'], {}),
  ev('ev7', 'akropolis', 'Echo Park', TODAY, '20:30', ['concert'], ['indie'], { first_seen: TODAY }),
  ev('ev8', 'roxy', 'Club Mix', TODAY, '23:00', ['party'], ['house', 'techno'], {}),
  ev('ev9', 'meetfactory', 'Open studio', TODAY, '18:00', ['opening'], [], {}),
  ev('ev10', 'akropolis', 'Jazz Night', TOMORROW, '20:00', ['concert'], ['jazz'], {}),
  ev('ev11', 'cross-club', 'Sunday Club', TOMORROW, '22:00', ['party'], ['techno'], {}),
]

const SYNTHETIC = { schema_version: 1, generated_at: FROZEN_ISO, venues: VENUES, events: EVENTS }

async function setup(page: any) {
  await page.clock.setFixedTime(FROZEN_ISO)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.removeItem('eventsPeriod')
    localStorage.removeItem('eventsSort')
  })
  await page.route('**/events.json', (route: any) => {
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(SYNTHETIC) })
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

async function openEvent(page: any, title: string) {
  await page.evaluate((t: string) => {
    const els = Array.from(document.querySelectorAll('*')) as HTMLElement[]
    for (const el of els) {
      if (el.children.length === 0 && el.textContent?.trim() === t) {
        const card = el.closest('[style*="border-radius"]') as HTMLElement
        if (card) { card.click(); return }
      }
    }
  }, title)
  await page.waitForTimeout(500)
}

test.describe('047', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('01-karta-stitok-typu', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    await page.screenshot({ path: path.join(OUT_DIR, '01-karta-stitok-typu.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 01-karta-stitok-typu.jpg')
  })

  test('02-akcia-bez-ceny', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    // Open an event without price (ev1 Nová Vlna)
    await openEvent(page, 'Nová Vlna – krst albumu')
    await page.screenshot({ path: path.join(OUT_DIR, '02-akcia-bez-ceny.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 02-akcia-bez-ceny.jpg')
  })

  test('03-akcia-vypredane-bez-ceny', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    // Open sold-out event without price (ev5 Hamlet remix)
    await openEvent(page, 'Hamlet remix')
    await page.screenshot({ path: path.join(OUT_DIR, '03-akcia-vypredane-bez-ceny.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 03-akcia-vypredane-bez-ceny.jpg')
  })

  test('04-panel-obdobia', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    // Open period sheet
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        if (b.textContent?.includes('Dnes') && b.getBoundingClientRect().height > 0) {
          b.click(); return
        }
      }
    })
    await page.waitForTimeout(400)
    await page.screenshot({ path: path.join(OUT_DIR, '04-panel-obdobia.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 04-panel-obdobia.jpg')
  })

  test('05-zoradenie-ponuka', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    // Switch to 7-day period first (sort is only shown for multi-day)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        if (b.textContent?.includes('Dnes') && b.getBoundingClientRect().height > 0) {
          b.click(); return
        }
      }
    })
    await page.waitForTimeout(300)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        if (b.textContent?.includes('7 dní')) { b.click(); return }
      }
    })
    await page.waitForTimeout(300)
    // Open sort menu
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        if (b.textContent?.includes('dátum') || b.textContent?.includes('Zoradiť')) {
          b.click(); return
        }
      }
    })
    await page.waitForTimeout(400)
    await page.screenshot({ path: path.join(OUT_DIR, '05-zoradenie-ponuka.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 05-zoradenie-ponuka.jpg')
  })
})
