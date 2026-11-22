import { test, expect, type Page } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 091: Pre teba with only types (own empty prompt), no Skip on the Types step,
// last type cannot be removed in Event preferences. Real events.json from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/091')
fs.mkdirSync(OUT_DIR, { recursive: true })

async function setup(page: Page, init: Record<string, string> = {}) {
  await page.addInitScript((init) => {
    if (!sessionStorage.getItem('init091')) {
      localStorage.clear()
      localStorage.setItem('language', 'sk')
      for (const [k, v] of Object.entries(init)) localStorage.setItem(k, v)
      sessionStorage.setItem('init091', '1')
    }
  }, init)
  await page.route('**/events.json', async (route: any) =>
    route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
}

const shot = (page: Page, name: string) =>
  page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80, scale: 'css' })

test.describe('091', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('Pre teba with only types; last type stays in Event preferences', async ({ page }) => {
    test.setTimeout(90000)
    await setup(page, { onboardingDone: '1', preferences: JSON.stringify({ types: ['concert', 'dj'], subtypes: [], genres: [] }) })
    await page.goto('')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.getByRole('button', { name: 'Pre teba', exact: true }).nth(1).click()
    const card = page.locator('[data-testid="for-you-setup"]')
    await expect(card).toHaveCount(1)
    await expect(card).toContainText('Pridaj obľúbené žánre alebo miesta')
    await page.waitForTimeout(800)
    await shot(page, 'for-you-types-only.jpg')

    await page.click('[data-testid="for-you-setup-btn"]')
    await page.waitForSelector('[data-testid="preferences-page"]')
    await page.click('[data-testid="pref-type-dj"] > button')
    await expect(page.locator('[data-testid="pref-type-dj"]')).not.toHaveAttribute('data-on', /.*/)
    await page.click('[data-testid="pref-type-concert"] > button')
    await expect(page.locator('[data-testid="pref-type-concert"]')).toHaveAttribute('data-shake', '1')
    await expect(page.locator('[data-testid="pref-type-concert"]')).toHaveAttribute('data-on', 'true')
    const stored = await page.evaluate(() => JSON.parse(localStorage.getItem('preferences') ?? '{}').types)
    expect(stored).toEqual(['concert'])
  })

  test('onboarding: no Skip on the Types step', async ({ page }) => {
    await setup(page)
    await page.goto('?dbg=onboarding')
    await page.click('[data-testid="onb-start"]')
    await page.waitForSelector('[data-testid="onb-step-places"]')
    await expect(page.locator('[data-testid="onb-step-skip"]')).toHaveCount(1)
    await page.locator('[data-testid^="pref-place-"]').nth(1).click()
    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-types"]')
    await expect(page.locator('[data-testid="onb-step-skip"]')).toHaveCount(0)
    await page.click('[data-testid="onb-next"]')
    await expect(page.locator('[data-testid="onb-next"]')).toHaveAttribute('data-shake', /\d/)
    await expect(page.locator('[data-testid="onb-step-types"]')).toHaveCount(1)
  })
})
