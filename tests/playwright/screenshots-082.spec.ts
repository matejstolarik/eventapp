import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 082: venue image as fallback for events without image.
// Real events.json and images from Pages; Akcie limited to Bike Jesus events.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/082')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-20T15:00:00'
const VENUE = 'bike-jesus'

async function setup(page: any) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('onboardingDone', '1')
    localStorage.setItem('favorites', '[]')
    localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'anytime' }))
  })
  await page.route('**/events.json', async (route: any) => {
    const res = await route.fetch({ url: PAGES + 'events.json' })
    const data = await res.json()
    data.events = data.events.filter((e: any) => e.venue_id === VENUE)
    await route.fulfill({ response: res, json: data })
  })
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
}

const shot = (page: any, name: string) =>
  page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80, scale: 'css' })

test.describe('082', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie bike jesus', async ({ page }) => {
    await setup(page)
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await shot(page, 'events-bike-jesus.jpg')
    const srcs = await page.locator('img').evaluateAll((els: any[]) => els.map(e => e.getAttribute('src')))
    expect(srcs.filter((s: string) => s && s.includes('img/venues/card/bike-jesus.jpg')).length).toBeGreaterThan(3)
  })

  test('event page with venue image', async ({ page, request }) => {
    const data = await (await request.get(PAGES + 'events.json')).json()
    const ev = data.events.find((e: any) => e.venue_id === VENUE && !e.image_thumb && e.date >= NOW.slice(0, 10))
    if (!ev) throw new Error('no Bike Jesus event without image')
    await setup(page)
    await page.goto(`/#/akcia/${ev.id}`)
    await page.waitForTimeout(3000)
    await shot(page, 'event-page-venue-image.jpg')
    await expect(page.locator('img[src*="img/venues/detail/bike-jesus.jpg"]')).toHaveCount(1)
    await expect(page.locator('text=Plagát')).toHaveCount(0)
  })
})
