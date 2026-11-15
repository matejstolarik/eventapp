import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/040')
fs.mkdirSync(OUT_DIR, { recursive: true })

// Sunday 2026-11-15 18:00
const FROZEN_ISO = '2026-11-15T18:00:00'
const TODAY = '2026-11-15'
const TOMORROW = '2026-11-16'
const FRI = '2026-11-20'
const SAT = '2026-11-21'
const SUN_NEXT = '2026-11-22'

const VENUES = [
  { id: 'akropolis', name: 'Palác Akropolis', lat: 50.0787, lng: 14.4592, character: ['alternative', 'underground'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Kubelíkova 27', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [] },
  { id: 'cross-club', name: 'Cross Club', lat: 50.1082927, lng: 14.4432281, character: ['underground', 'late-night'], type: ['dance-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Plynární 23', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [] },
  { id: 'roxy', name: 'ROXY', lat: 50.0882, lng: 14.4252, character: ['alternative', 'late-night'], type: ['concert-club'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Dlouhá 33', city: 'Praha', size: 'large', sources: [], description: null, description_url: null, image_source: null, music: [] },
  { id: 'meetfactory', name: 'MeetFactory', lat: 50.0506, lng: 14.4034, character: ['art-space', 'alternative'], type: ['art-space'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Ke Sklárně 15', city: 'Praha', size: 'medium', sources: [], description: null, description_url: null, image_source: null, music: [] },
  { id: 'archa', name: 'Archa+', lat: 50.0901, lng: 14.4204, character: ['english-friendly', 'experimental'], type: ['theatre'], image_url: null, image_thumb: null, active: true, web: '', ra_url: null, instagram: null, address: 'Na Poříčí 26', city: 'Praha', size: 'small', sources: [], description: null, description_url: null, image_source: null, music: [] },
]

function ev(id: string, venue_id: string, title: string, date: string, start_time: string, formats: string[], genres: string[]): object {
  return {
    id, venue_id, title, date, start_time, end_time: null, doors_time: null,
    formats, genres, character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [{ type: 'rss', url: 'https://example.com' }],
    classification: null, first_seen: TODAY, last_seen: TODAY, status: 'scheduled', flags: []
  }
}

const EVENTS = [
  ev('ev1', 'akropolis', 'Nová Vlna – krst albumu', TODAY, '20:00', ['concert'], ['indie', 'post-punk']),
  ev('ev2', 'cross-club', 'Lumen all night long', TODAY, '22:00', ['dj'], ['house', 'techno']),
  ev('ev3', 'roxy', 'Párty 2000s', TODAY, '22:00', ['party'], ['pop', 'disco']),
  ev('ev4', 'meetfactory', 'Mesto a my: diskusia', TODAY, '19:00', ['talk'], []),
  ev('ev5', 'archa', 'Hamlet remix', TODAY, '20:00', ['theatre'], []),
  ev('ev6', 'cross-club', 'Bass Shift', TODAY, '23:00', ['dj'], ['drum-and-bass']),
  ev('ev7', 'akropolis', 'Echo Park', TODAY, '20:30', ['concert'], ['indie']),
  ev('ev8', 'roxy', 'Club Mix', TODAY, '23:00', ['party'], ['house', 'techno']),
  ev('ev9', 'meetfactory', 'Open studio', TODAY, '18:00', ['opening'], []),
  // Tomorrow
  ev('ev10', 'akropolis', 'Jazz Night', TOMORROW, '20:00', ['concert'], ['jazz']),
  ev('ev11', 'cross-club', 'Sunday Club', TOMORROW, '22:00', ['party'], ['techno']),
  // Weekend
  ev('ev12', 'roxy', 'Friday Rock', FRI, '21:00', ['concert'], ['rock']),
  ev('ev13', 'cross-club', 'Sobotné vibrácie', SAT, '23:00', ['dj'], ['techno']),
  ev('ev14', 'archa', 'Divadelný víkend', SUN_NEXT, '17:00', ['theatre'], []),
]

const SYNTHETIC = {
  generated_at: '2026-11-15T13:00:00',
  venues: VENUES,
  events: EVENTS,
}

// Empty events for empty state test
const EMPTY_EVENTS = { ...SYNTHETIC, events: [] }

async function setup(page: any, events = SYNTHETIC) {
  await page.clock.setFixedTime(FROZEN_ISO)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    // Clear any stored period
    localStorage.removeItem('eventsPeriod')
  })
  await page.route('**/events.json', (route: any) => {
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(events) })
  })
}

async function goToEvents(page: any) {
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(1500)
  // Click Akcie tab (2nd tab from left)
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

test.describe('040', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('01-akcie-dnes', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    await page.screenshot({ path: path.join(OUT_DIR, '01-akcie-dnes.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 01-akcie-dnes.jpg')
  })

  test('02-akcie-obdobie', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    // Click the period button
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        if (b.textContent?.includes('Dnes') && b.style.background?.includes('F4F2FF')) {
          b.click()
          return
        }
      }
      // Fallback: first button with white background
      const wb = buttons.find(b => b.getBoundingClientRect().top < 180 && b.getBoundingClientRect().top > 100)
      if (wb) wb.click()
    })
    await page.waitForTimeout(400)
    await page.screenshot({ path: path.join(OUT_DIR, '02-akcie-obdobie.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 02-akcie-obdobie.jpg')
  })

  test('03-akcie-kalendar-interval', async ({ page }) => {
    await setup(page)
    await goToEvents(page)
    // Open period sheet
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      const wb = buttons.find(b => b.getBoundingClientRect().top < 180 && b.getBoundingClientRect().top > 100)
      if (wb) wb.click()
    })
    await page.waitForTimeout(400)
    // Click "Iný dátum" (last item in sheet)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        if (b.textContent?.includes('Iný dátum')) { b.click(); return }
      }
    })
    await page.waitForTimeout(300)
    // Click day 20 (Friday)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        const rect = b.getBoundingClientRect()
        if (b.textContent?.trim() === '20' && rect.top > 500) { b.click(); return }
      }
    })
    await page.waitForTimeout(200)
    await page.screenshot({ path: path.join(OUT_DIR, '03-akcie-kalendar-interval.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 03-akcie-kalendar-interval.jpg')
  })

  test('04-mapa-vyber-dna', async ({ page }) => {
    await setup(page)
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(1500)
    // Click the day button (Dnes ▾ in top bar)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      for (const b of buttons) {
        const rect = b.getBoundingClientRect()
        if (rect.top < 90 && rect.top > 40 && rect.left < 80) {
          b.click(); return
        }
      }
    })
    await page.waitForTimeout(400)
    await page.screenshot({ path: path.join(OUT_DIR, '04-mapa-vyber-dna.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 04-mapa-vyber-dna.jpg')
  })

  test('05-akcie-prazdne', async ({ page }) => {
    await setup(page, EMPTY_EVENTS)
    await goToEvents(page)
    await page.screenshot({ path: path.join(OUT_DIR, '05-akcie-prazdne.jpg'), type: 'jpeg', quality: 80 })
    console.log('✓ 05-akcie-prazdne.jpg')
  })
})
