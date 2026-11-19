import { test, expect, type Page } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 080: onboarding polish, Pre teba without preferences, Event preferences.
// Real events.json from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/080')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T19:00:00'

async function setup(page: Page, init: Record<string, string> = {}) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript((init) => {
    if (!sessionStorage.getItem('init080')) {
      localStorage.clear()
      localStorage.setItem('language', 'sk')
      for (const [k, v] of Object.entries(init)) localStorage.setItem(k, v)
      sessionStorage.setItem('init080', '1')
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

/** Next without a pick: the button shakes and the step stays. */
async function expectNoAdvance(page: Page, step: string) {
  await page.click('[data-testid="onb-next"]')
  await expect(page.locator('[data-testid="onb-next"]')).toHaveAttribute('data-shake', /\d/)
  await expect(page.locator(`[data-testid="onb-step-${step}"]`)).toHaveCount(1)
}

test.describe('080', () => {
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
    await expectNoAdvance(page, 'places')
    const places = page.locator('[data-testid^="pref-place-"]')
    await places.nth(1).click()
    await places.nth(3).click()
    await page.waitForTimeout(1200)
    await shot(page, 'onb-2-places.jpg')

    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-types"]')
    await expectNoAdvance(page, 'types')
    // DJ and culture picked and deselected again: must look never picked
    const before = await page.locator('[data-testid="pref-type-culture"]').evaluate(el => getComputedStyle(el).boxShadow)
    await page.click('[data-testid="pref-type-dj"] > button')
    await page.click('[data-testid="pref-type-culture"] > button')
    await page.waitForTimeout(400)
    await page.click('[data-testid="pref-type-dj"] > button')
    await page.click('[data-testid="pref-type-culture"] > button')
    await page.waitForTimeout(600)
    for (const tp of ['dj', 'culture']) {
      const s = await page.locator(`[data-testid="pref-type-${tp}"]`).evaluate(el => getComputedStyle(el).boxShadow)
      expect(s).toBe(before)
    }
    const subH = await page.locator('[data-testid="pref-subtypes"]').evaluate(el => el.getBoundingClientRect().height)
    expect(subH).toBe(0)
    await shot(page, 'onb-3-types-deselected.jpg')

    await page.click('[data-testid="pref-type-concert"] > button')
    await page.click('[data-testid="pref-type-dj"] > button')
    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-genres"]')
    await expectNoAdvance(page, 'genres')
    for (const g of ['techno', 'drum-and-bass', 'punk']) await page.click(`[data-testid="pref-genre-${g}"]`)
    await page.click('[data-testid="onb-next"]')
    await page.waitForSelector('[data-testid="onb-step-done"]')
    await page.waitForTimeout(400)
    // Done: same left column, control centred; 4 rows (2 with ✦) and 4 -> 2 rows
    const ctl = page.locator('[data-testid="onb-done-control"]')
    const [a, b] = [await ctl.nth(0).boundingBox(), await ctl.nth(1).boundingBox()]
    expect(a!.x).toBe(b!.x); expect(a!.width).toBe(b!.width)
    await expect(page.locator('[data-testid="onb-done-for-you"] [data-testid="onb-mini-row"]')).toHaveCount(4)
    await expect(page.locator('[data-testid="onb-done-for-you"] [data-testid="onb-mini-sparkle"]')).toHaveCount(2)
    await expect(page.locator('[data-testid="onb-done-filter"] [data-testid="onb-mini-row"]')).toHaveCount(6)
    const chipW = await page.locator('[data-testid="onb-done-for-you"] [data-testid="onb-done-control"] button').evaluate(el => el.getBoundingClientRect().width)
    expect(chipW).toBeLessThanOrEqual(a!.width)
    await shot(page, 'onb-5-done.jpg')
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
    await expect(page.locator('[data-testid="onb-skip-toast"]')).toContainText('Preferencie akcií')
    await page.unrouteAll({ behavior: 'ignoreErrors' })
  })

  test('Pre teba without preferences, Event preferences page', async ({ page }) => {
    test.setTimeout(90000)
    await setup(page, { onboardingDone: '1' })
    await page.goto('')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.getByRole('button', { name: 'Pre teba', exact: true }).nth(1).click()
    await expect(page.locator('[data-testid="for-you-setup"]')).toHaveCount(1)
    await expect(page.locator('[data-testid="setup-prompt"]')).toHaveCount(0)
    await page.waitForTimeout(800)
    const card = await page.locator('[data-testid="for-you-setup"]').boundingBox()
    console.log('setup card box', JSON.stringify(card))
    await shot(page, 'events-for-you-empty.jpg')

    await page.click('[data-testid="for-you-setup-btn"]')
    await page.waitForSelector('[data-testid="preferences-page"]')
    await expect(page.locator('[data-testid="preferences-page"] h1')).toContainText('Preferencie akcií')
    const order = await page.locator('[data-testid^="pref-section-"]').evaluateAll(els => els.map(e => e.getAttribute('data-testid')))
    expect(order).toEqual(['pref-section-types', 'pref-section-genres', 'pref-section-places'])
    await page.waitForTimeout(1000)
    await shot(page, 'preferences.jpg')

    // pick a favourite place, close with the tick -> the list shows events for you
    await page.locator('[data-testid^="pref-place-"]').first().click()
    await page.click('[data-testid="pref-type-dj"] > button')
    await page.click('[data-testid="preferences-done"]')
    await expect(page.locator('[data-testid="preferences-page"]')).toHaveCount(0)
    await expect(page.locator('[data-testid="for-you-setup"]')).toHaveCount(0)
    await page.unrouteAll({ behavior: 'ignoreErrors' })
  })
})
