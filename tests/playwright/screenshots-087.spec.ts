import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 087: Akcie with model preferences (DJ + concert; techno, punk, rock;
// favourites Fuchs2 + Cross Club), events.json from Pages, day 2026-11-28
// (2 events ✦✦ and 2 ✦). The Pre teba chip is tapped so the sort switches by itself.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/087')
fs.mkdirSync(OUT_DIR, { recursive: true })

test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

test('087 for you best match + sort menu', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('onboardingDone', '1')
    localStorage.setItem('favorites', JSON.stringify(['fuchs2', 'cross-club']))
    localStorage.setItem('preferences', JSON.stringify({ types: ['dj', 'concert'], subtypes: [], genres: ['techno', 'punk', 'rock'] }))
    localStorage.setItem('eventsFilters', JSON.stringify({ forYou: false, isNew: false }))
    localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'anytime' }))
  })
  await page.route('**/events.json', async (route: any) => {
    // custom periods are not stored → Kedykoľvek over events.json narrowed to 2026-11-28
    const res = await route.fetch({ url: PAGES + 'events.json' })
    const data = await res.json()
    data.events = data.events.filter((e: any) => e.date === '2026-11-28')
    await route.fulfill({ response: res, json: data })
  })
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
  await page.goto('/#/akcie')
  await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
  await page.getByRole('button', { name: /Pre teba/ }).filter({ visible: true }).last().click({ force: true })
  await expect(page.getByText('najlepšia zhoda').first()).toBeVisible()
  await expect(page.locator('[data-foryou-tier="2"]').first()).toBeVisible()
  await expect(page.locator('[data-foryou-tier="1"]').first()).toBeVisible()
  await page.waitForTimeout(2500)
  const a = path.join(OUT_DIR, 'events-for-you-best-match.jpg')
  await page.screenshot({ path: a, type: 'jpeg', quality: 80, scale: 'css' })

  await page.getByText('Zoradiť').first().click()
  await page.waitForTimeout(500)
  const b = path.join(OUT_DIR, 'sort-menu-for-you.jpg')
  await page.screenshot({ path: b, type: 'jpeg', quality: 80, scale: 'css' })
  expect(fs.existsSync(a) && fs.existsSync(b)).toBeTruthy()
})
