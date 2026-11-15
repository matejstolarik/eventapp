import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/036')
fs.mkdirSync(OUT_DIR, { recursive: true })

const TODAY = '2026-11-15'
const FROZEN_ISO = '2026-11-15T14:00:00'

// Two venues: one favored (cross-club), one not (roxy)
const SYNTHETIC_EVENTS = {
  generated_at: '2026-11-15T13:00:00',
  venues: [
    {
      id: 'cross-club', name: 'Cross Club', lat: 50.1082927, lng: 14.4432281,
      character: ['underground', 'late-night'], type: ['dance-club'],
      image_url: null, image_thumb: null,
      active: true, web: '', ra_url: null, instagram: null, address: 'Plynární 1096/23',
      city: 'Praha', size: 'medium', sources: [], description: null, description_url: null,
      image_source: null, music: []
    },
    {
      id: 'roxy', name: 'ROXY', lat: 50.0882, lng: 14.4252,
      character: ['alternative', 'late-night'], type: ['concert-club'],
      image_url: null, image_thumb: null,
      active: true, web: '', ra_url: null, instagram: null, address: 'Dlouhá 33',
      city: 'Praha', size: 'medium', sources: [], description: null, description_url: null,
      image_source: null, music: []
    },
  ],
  events: [
    {
      id: 'ev-cc-1', venue_id: 'cross-club', title: 'Techno',
      date: TODAY, start_time: '22:00', end_time: null,
      formats: ['dj'], genres: ['techno'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://crossclub.cz' }],
      classification: null, first_seen: TODAY, last_seen: TODAY, status: 'scheduled', flags: []
    },
    {
      id: 'ev-roxy-1', venue_id: 'roxy', title: 'ROXY Night',
      date: TODAY, start_time: '21:00', end_time: null,
      formats: ['concert'], genres: ['indie'], character: [],
      artists: [], price_text: null, free: null, sold_out: null, room: null,
      ticket_url: null, image_url: null, description: null, description_source: null,
      sources: [{ type: 'rss', url: 'https://roxy.cz' }],
      classification: null, first_seen: TODAY, last_seen: TODAY, status: 'scheduled', flags: []
    },
  ]
}

// Synthetic data with image_thumb URLs for the Places screenshot
const EVENTS_WITH_THUMBS = {
  ...SYNTHETIC_EVENTS,
  venues: [
    {
      ...SYNTHETIC_EVENTS.venues[0],
      image_thumb: 'img/venues/cross-club.jpg',
    },
    {
      ...SYNTHETIC_EVENTS.venues[1],
      image_thumb: null,
    },
  ]
}

async function setupPage(page: any, events = SYNTHETIC_EVENTS) {
  await page.clock.setFixedTime(FROZEN_ISO)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
  })
  await page.route('**/events.json', (route: any) => {
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(events) })
  })
  // Serve a tiny placeholder image for the thumb
  await page.route('**/img/venues/**', (route: any) => {
    // 1x1 orange JPEG
    const tiny = Buffer.from(
      '/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8U' +
      'HRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgN' +
      'DRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIy' +
      'MjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAA' +
      'AAAAAAAAAAAAAAAAAP/EABQBAQAAAAAAAAAAAAAAAAAAAAD/xAAUEQEAAAAAAAAAAAAAAAAA' +
      'AAAA/9oADAMBAAIRAxEAPwCwABmX/9k=',
      'base64'
    )
    route.fulfill({ contentType: 'image/jpeg', body: tiny })
  })
}

async function waitForMap(page: any) {
  await page.goto('/')
  await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
  await page.waitForTimeout(2000)
}

test.describe('036', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  /**
   * Part 1: pin reappears after quick toggle (exit → return within 100ms → still visible at 400ms)
   * We use the favorites toggle to trigger updateMarkers twice quickly.
   */
  test('pin-cancel-leave: reappears after quick re-add', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('language', 'sk')
      // roxy is NOT favored; cross-club IS
      localStorage.setItem('favorites', JSON.stringify(['cross-club']))
    })
    await page.clock.setFixedTime(FROZEN_ISO)
    await page.route('**/events.json', (route: any) => {
      route.fulfill({ contentType: 'application/json', body: JSON.stringify(SYNTHETIC_EVENTS) })
    })
    await waitForMap(page)

    // Both pins should be visible (not in favorites mode yet)
    const roxyPin = page.locator('.pin-inner').nth(1)
    await expect(roxyPin).toBeVisible()

    // Find the favorites toggle button (top-right area of the map bar)
    // Click it to show only favored venues → roxy starts leaving
    // Then click it back within 100ms → roxy should come back
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      // The heart/favorites toggle is in the top bar, right side
      for (const b of buttons) {
        const rect = b.getBoundingClientRect()
        if (rect.top < 90 && rect.top > 10 && rect.height > 20 && rect.height < 60 && rect.right > 300) {
          b.click()
          return
        }
      }
    })
    // Within 100ms, toggle back
    await page.waitForTimeout(80)
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

    // After 400ms (well past the 250ms cleanup timer), roxy pin must still be in DOM and attached
    await page.waitForTimeout(400)
    const pinCount = await page.evaluate(() => {
      // Count .maplibregl-marker elements that are still attached
      return document.querySelectorAll('.maplibregl-marker').length
    })
    expect(pinCount).toBeGreaterThanOrEqual(2)
  })

  /**
   * Part 3: screenshot of Places list with thumbnails
   */
  test('01-miesta', async ({ page }) => {
    await setupPage(page, EVENTS_WITH_THUMBS)
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(1500)

    // Navigate to Miesta tab (3rd tab from left in bottom bar)
    await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[]
      const tabBtns = buttons.filter(b => {
        const rect = b.getBoundingClientRect()
        return rect.bottom > 740 && rect.top > 700
      })
      if (tabBtns[2]) tabBtns[2].click()
    })
    await page.waitForTimeout(800)

    await page.screenshot({
      path: path.join(OUT_DIR, '01-miesta.jpg'),
      type: 'jpeg',
      quality: 80
    })
    console.log('✓ 01-miesta.jpg')
  })
})
