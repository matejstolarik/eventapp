import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 076: culture genre rows in the filter, full `alternative` tag.
// Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/076')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T17:00:00'

async function setup(page: any, opts: { period?: object; filter?: object } = {}) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript(([period, filter]: [string, string | null]) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('favorites', '[]')
    localStorage.setItem('eventsPeriod', period)
    if (filter) localStorage.setItem('filter', filter)
    else localStorage.removeItem('filter')
  }, [JSON.stringify(opts.period ?? { type: 'next7' }), opts.filter ? JSON.stringify(opts.filter) : null])
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

async function openFilter(page: any) {
  await page.locator('button[aria-label^="Filter"]:visible').last().click()
  await page.waitForSelector('[data-testid="filter-sheet"]')
  await page.waitForTimeout(400)
}

test.describe('076', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('filter-film-divadlo', async ({ page }) => {
    await setup(page, { period: { type: 'next30' } })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await openFilter(page)
    await page.locator('[data-testid="filter-subtypes"] > button', { hasText: 'film' }).click()
    await page.locator('[data-testid="filter-subtypes"] > button', { hasText: 'theatre' }).click()
    await page.waitForTimeout(300)
    await expect(page.locator('[data-testid="filter-culture-genres-film"]')).toHaveCount(1)
    await expect(page.locator('[data-testid="filter-culture-genres-theatre"]')).toHaveCount(1)
    const rows = await page.evaluate(() => ['film', 'theatre'].map(s =>
      [...document.querySelectorAll(`[data-testid="filter-culture-genres-${s}"] button`)].map(b => b.textContent)))
    await shot(page, 'filter-film-divadlo.jpg')
    // Badge: 2 subtypes + 1 culture genre
    await page.locator('[data-testid="filter-culture-genres-film"] button').first().click()
    await page.locator('[data-testid="filter-show"]').click()
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(0, { timeout: 2000 })
    const badge = await page.locator('[data-testid="filter-badge"]:visible').first().textContent()
    fs.writeFileSync(path.join(OUT_DIR, 'riadky.json'), JSON.stringify({ film: rows[0], theatre: rows[1], badge }, null, 2))
  })

  test('miesto-alternative', async ({ page }) => {
    await setup(page)
    await page.goto('/#/miesto/cross-club')
    await page.waitForSelector('text=alternative', { timeout: 15000 })
    await page.waitForTimeout(2000)
    await expect(page.locator('text=/^alt$/')).toHaveCount(0)
    await shot(page, 'miesto-alternative.jpg')
  })
})
