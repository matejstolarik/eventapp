import { test, expect, type Page } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 079: onboarding, preferences, Pre teba. Real events.json from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/079')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T19:00:00'

async function setup(page: Page) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript(() => {
    if (!sessionStorage.getItem('init079')) {
      localStorage.clear()
      localStorage.setItem('language', 'sk')
      sessionStorage.setItem('init079', '1')
    }
  })
  await page.route('**/events.json', async (route: any) =>
    route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
}

const shot = (page: Page, name: string) =>
  page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80, scale: 'css' })

test.describe('079', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('onboarding flow', async ({ page }) => {
    test.setTimeout(120000)
    await setup(page)
    await page.goto('?dbg=onboarding')
    await page.waitForSelector('[data-testid="onb-step-welcome"]', { timeout: 15000 })
    await page.waitForTimeout(800)
    await shot(page, 'onb-1-welcome.jpg')

    await page.click('[data-testid="onb-start"]')
    await page.waitForSelector('[data-testid="onb-step-places"]')
    const places = page.locator('[data-testid^="pref-place-"]')
    await places.nth(1).click()
    await places.nth(3).click()
    await page.waitForTimeout(1200)
    await shot(page, 'onb-2-places.jpg')

    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-types"]')
    await page.click('[data-testid="pref-type-concert"] > button')
    await page.click('[data-testid="pref-type-dj"] > button')
    await page.click('[data-testid="pref-type-culture"] > button')
    await page.waitForTimeout(400)
    await page.click('[data-testid="pref-subtype-film"]')
    await page.click('[data-testid="pref-subtype-talk"]')
    await page.waitForTimeout(400)
    await shot(page, 'onb-3-types.jpg')

    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-genres"]')
    for (const g of ['techno', 'drum-and-bass', 'punk']) await page.click(`[data-testid="pref-genre-${g}"]`)
    await expect(page.locator('[data-testid="pref-genre-count"]')).toHaveText('3/5')
    await page.waitForTimeout(400)
    await shot(page, 'onb-4-genres.jpg')

    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-done"]')
    await page.waitForTimeout(400)
    await shot(page, 'onb-5-done.jpg')

    const prefs = await page.evaluate(() => ({ favorites: localStorage.getItem('favorites'), preferences: localStorage.getItem('preferences') }))
    fs.writeFileSync(path.join(OUT_DIR, 'prefs.json'), JSON.stringify(prefs, null, 2))

    await page.click('[data-testid="onb-finish"]')
    await expect(page.locator('[data-testid="onboarding"]')).toHaveCount(0)
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await expect(page.locator('nav button[aria-current="page"]')).toHaveAttribute('aria-label', 'Akcie')
    // compact bar copy comes first in the DOM; the expanded header chip is the second
    await page.getByRole('button', { name: 'Pre teba', exact: true }).nth(1).click()
    await page.waitForTimeout(2500)
    await shot(page, 'events-for-you.jpg')

    await page.locator('nav button[aria-label="Môj účet"]').click()
    await page.click('[data-testid="account-preferences"]')
    await page.waitForSelector('[data-testid="preferences-page"]')
    await page.waitForTimeout(1200)
    await shot(page, 'account-preferences.jpg')
    await page.unrouteAll({ behavior: 'ignoreErrors' })
  })

  test('skip confirm', async ({ page }) => {
    await setup(page)
    await page.goto('?dbg=onboarding')
    await page.waitForSelector('[data-testid="onb-step-welcome"]', { timeout: 15000 })
    await page.click('[data-testid="onb-skip"]')
    await page.waitForSelector('[data-testid="onb-skip-confirm"]')
    await page.waitForTimeout(500)
    await shot(page, 'onb-skip-confirm.jpg')
    await page.click('[data-testid="onb-skip-confirm-btn"]')
    await expect(page.locator('[data-testid="onboarding"]')).toHaveCount(0)
    await expect(page.locator('[data-testid="onb-skip-toast"]')).toHaveCount(1)
    await page.unrouteAll({ behavior: 'ignoreErrors' })
  })

  test('new install shows onboarding, existing user does not', async ({ page }) => {
    test.setTimeout(60000)
    await page.clock.setFixedTime(NOW)
    await page.route('**/events.json', async (route: any) =>
      route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
    await page.goto('')
    await page.evaluate(() => localStorage.clear())
    await page.reload()
    await expect(page.locator('[data-testid="onb-step-welcome"]')).toHaveCount(1, { timeout: 15000 })
    await page.evaluate(() => { localStorage.clear(); localStorage.setItem('favorites', '["x"]'); localStorage.setItem('language', 'sk') })
    await page.reload()
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await expect(page.locator('[data-testid="onboarding"]')).toHaveCount(0)
  })
})
