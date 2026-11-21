import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 085: Akcie, Kedykoľvek, only the new venues (events.json from Pages
// filtered to Lucerna Music Bar, O2 arena, O2 universum, Jazz Republic).
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/085')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NEW = ['lucerna-music-bar', 'o2-arena', 'o2-universum', 'jazz-republic']

test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

test('085 events new venues', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('onboardingDone', '1')
    localStorage.setItem('favorites', '[]')
    localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'anytime' }))
  })
  await page.route('**/events.json', async (route: any) => {
    const res = await route.fetch({ url: PAGES + 'events.json' })
    const data = await res.json()
    data.events = data.events.filter((e: any) => NEW.includes(e.venue_id))
    await route.fulfill({ response: res, json: data })
  })
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
  await page.goto('/#/akcie')
  await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
  await page.waitForTimeout(3000)
  await page.screenshot({ path: path.join(OUT_DIR, 'events-new-venues.jpg'), type: 'jpeg', quality: 80, scale: 'css' })
  expect(fs.existsSync(path.join(OUT_DIR, 'events-new-venues.jpg'))).toBeTruthy()
})
