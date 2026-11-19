import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 073: sort by venue size. Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/073')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T17:00:00'

async function setup(page: any) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('favorites', '[]')
    localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'next7' }))
  })
  await page.route('**/events.json', async (route: any) =>
    route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    route.fulfill({ response: await route.fetch({ url: PAGES + rel }) })
  })
}

async function shot(page: any, name: string) {
  await page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80, scale: 'css' })
}

test.describe('073', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('zoradit-ponuka and akcie-velkost', async ({ page }) => {
    await setup(page)
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await page.getByRole('button', { name: /Zoradiť/ }).click()
    await page.waitForSelector('button:has-text("veľkosť")')
    await page.waitForTimeout(400)
    await shot(page, 'zoradit-ponuka.jpg')
    await page.locator('button:has-text("veľkosť")').click()
    await page.waitForTimeout(2500)
    await shot(page, 'akcie-velkost.jpg')
  })
})
