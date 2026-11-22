import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 089: Akcie, Kedykoľvek, only the new venues (events.json from Pages
// filtered to Karlovy Lazne, Cafe V Lese, Klub 007, OX Club, Kampus Hybernska).
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/089')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NEW = ['karlovy-lazne', 'cafe-v-lese', 'klub-007-strahov', 'ox-club', 'kampus-hybernska']

test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

test('089 events new venues', async ({ page }) => {
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
