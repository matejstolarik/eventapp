import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 077: count row at "Kedykoľvek", type help card in the filter.
// Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/077')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T17:00:00'

async function setup(page: any, period: object) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript((p: string) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('favorites', '[]')
    localStorage.setItem('eventsPeriod', p)
    localStorage.removeItem('filter')
  }, JSON.stringify(period))
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

test.describe('077', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie-kedykolvek', async ({ page }) => {
    await setup(page, { type: 'anytime' })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    const row = page.getByText(/^\d+ akci/).first()
    await expect(row).toBeVisible()
    fs.writeFileSync(path.join(OUT_DIR, 'pocet.txt'), (await row.textContent()) ?? '')
    await shot(page, 'akcie-kedykolvek.jpg')
  })

  test('filter-typy-help', async ({ page }) => {
    await setup(page, { type: 'next7' })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2000)
    await page.locator('button[aria-label^="Filter"]:visible').last().click()
    await page.waitForSelector('[data-testid="filter-sheet"]')
    await page.waitForTimeout(400)
    const help = page.locator('[data-testid="filter-type-help"]')
    const box = await help.boundingBox()
    expect(box!.width).toBeGreaterThanOrEqual(44)
    expect(box!.height).toBeGreaterThanOrEqual(44)
    await help.click()
    const card = page.locator('[data-testid="filter-type-help-card"]')
    await expect(card).toContainText('Interpret alebo kapela hrá svoju hudbu naživo.')
    await expect(card).toContainText('kvôli čomu tam ľudia idú.')
    await page.waitForTimeout(400)
    await shot(page, 'filter-typy-help.jpg')
    // System Back closes only the card
    await page.goBack()
    await expect(card).toHaveCount(0, { timeout: 2000 })
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(1)
    // Cross closes the card, filter stays; Back then closes the filter
    await help.click()
    await page.locator('[data-testid="filter-type-help-close"]').click()
    await expect(card).toHaveCount(0, { timeout: 2000 })
    await page.waitForTimeout(300)
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(1)
    // Tap outside the card
    await help.click()
    await page.mouse.click(10, 10)
    await expect(card).toHaveCount(0, { timeout: 2000 })
    await page.waitForTimeout(300)
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(1)
    await page.goBack()
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(0, { timeout: 2000 })
    await expect(page).toHaveURL(/#\/akcie/)
  })
})
