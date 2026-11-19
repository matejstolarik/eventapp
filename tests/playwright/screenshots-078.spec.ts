import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 078: talk selected in the filter shows the row of talk genres.
// Real events.json from Pages (after the pipeline run).
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/078')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T17:00:00'

test.describe('078', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('filter-talk', async ({ page }) => {
    await page.clock.setFixedTime(NOW)
    await page.addInitScript(() => {
      localStorage.setItem('language', 'sk')
      localStorage.setItem('favorites', '[]')
      localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'next30' }))
      localStorage.removeItem('filter')
    })
    await page.route('**/events.json', async (route: any) =>
      route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
    await page.route(/\/eventapp\/img\//, async (route: any) => {
      const rel = route.request().url().split('/eventapp/')[1]
      route.fulfill({ response: await route.fetch({ url: PAGES + rel }) })
    })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await page.locator('button[aria-label^="Filter"]:visible').last().click()
    await page.waitForSelector('[data-testid="filter-sheet"]')
    await page.waitForTimeout(400)
    await page.locator('[data-testid="filter-subtypes"] > button', { hasText: 'talk' }).click()
    await page.waitForTimeout(300)
    const row = page.locator('[data-testid="filter-culture-genres-talk"]')
    await expect(row).toHaveCount(1)
    await row.scrollIntoViewIfNeeded()
    const chips = await row.locator('button').allTextContents()
    fs.writeFileSync(path.join(OUT_DIR, 'talk-chips.txt'), chips.join('\n'))
    await page.waitForTimeout(300)
    await page.screenshot({ path: path.join(OUT_DIR, 'filter-talk.jpg'), type: 'jpeg', quality: 80, scale: 'css' })
  })
})
