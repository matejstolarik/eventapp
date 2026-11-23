import { test, expect, type Page } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 092: Cross Club profile with its own description. Real events.json from Pages
// (after the pipeline run that publishes `descriptions`).
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/092')
fs.mkdirSync(OUT_DIR, { recursive: true })

async function setup(page: Page) {
  await page.addInitScript(() => {
    if (!sessionStorage.getItem('init092s')) {
      localStorage.clear()
      localStorage.setItem('language', 'sk')
      localStorage.setItem('onboardingDone', '1')
      sessionStorage.setItem('init092s', '1')
    }
  })
  await page.route('**/events.json', async (route: any) =>
    route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
}

test.describe('092', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('Cross Club profile with description', async ({ page }) => {
    test.setTimeout(60000)
    await setup(page)
    await page.goto('#/miesto/cross-club')
    await expect(page.locator('text=Klub v Holešoviciach').first()).toBeVisible({ timeout: 20000 })
    await page.waitForTimeout(1200)
    await page.screenshot({ path: path.join(OUT_DIR, 'venue-description.jpg'), type: 'jpeg', quality: 80, scale: 'css' })
  })
})
