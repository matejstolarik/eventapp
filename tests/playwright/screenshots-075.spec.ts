import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 075: filter panel (Akcie and map), pins by filter, empty result.
// Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/075')
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

test.describe('075', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('filter-akcie, filter-kultura, smoothness, back closes', async ({ page }) => {
    await setup(page)
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)

    // Open animation: time from click until the panel stops moving
    const t0 = Date.now()
    await page.locator('button[aria-label^="Filter"]:visible').last().click()
    await page.waitForSelector('[data-testid="filter-sheet"]')
    await page.waitForFunction(() => {
      const el = document.querySelector('[data-testid="filter-sheet"]') as HTMLElement
      return el && getComputedStyle(el).transform.endsWith(', 0)') && el.getBoundingClientRect().top <= 115
    })
    const openMs = Date.now() - t0
    await page.waitForTimeout(300)
    await shot(page, 'filter-akcie.jpg')

    // Culture subtype chosen
    await page.locator('[data-testid="filter-subtypes"] button', { hasText: 'theatre' }).click()
    await page.waitForTimeout(300)
    await shot(page, 'filter-kultura.jpg')

    // Smoothness: expand all genres, scroll the content and measure frame gaps
    const all = page.locator('button', { hasText: /^Všetky \(\d+\) ›$/ })
    if (await all.count()) await all.click()
    const frames = await page.evaluate(async () => {
      const el = document.querySelector('[data-testid="filter-scroll"]') as HTMLElement
      const gaps: number[] = []
      let last = performance.now()
      let run = true
      const loop = (t: number) => { gaps.push(t - last); last = t; if (run) requestAnimationFrame(loop) }
      requestAnimationFrame(loop)
      for (let i = 0; i < 40; i++) { el.scrollTop += 25; await new Promise(r => setTimeout(r, 16)) }
      for (let i = 0; i < 40; i++) { el.scrollTop -= 25; await new Promise(r => setTimeout(r, 16)) }
      run = false
      gaps.shift()
      const sorted = [...gaps].sort((a, b) => a - b)
      return { frames: gaps.length, maxMs: Math.round(Math.max(...gaps)), p95Ms: Math.round(sorted[Math.floor(sorted.length * 0.95)]!), scrollHeight: el.scrollHeight, clientHeight: el.clientHeight, chips: el.querySelectorAll('button').length }
    })

    // System Back closes the panel
    await page.goBack()
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(0, { timeout: 2000 })
    // Badge: theatre subtype = 1
    await expect(page.locator('[data-testid="filter-badge"]:visible').first()).toHaveText('1')
    fs.writeFileSync(path.join(OUT_DIR, 'plynulost.json'), JSON.stringify({ openMs, ...frames }, null, 2))
  })

  test('filter-mapa and mapa-po-filtri', async ({ page }) => {
    await setup(page)
    await page.goto('/#/mapa')
    await page.waitForSelector('.pin-inner', { timeout: 20000 })
    await page.waitForTimeout(3000)
    const pinsBefore = await page.locator('.maplibregl-marker .pin-inner').count()
    await openFilter(page)
    await shot(page, 'filter-mapa.jpg')
    await page.locator('[data-testid="filter-type-concert"]').click()
    await page.waitForTimeout(200)
    await page.locator('[data-testid="filter-show"]').click()
    await page.waitForTimeout(1500)
    await expect(page.locator('[data-testid="filter-sheet"]')).toHaveCount(0)
    await shot(page, 'mapa-po-filtri.jpg')
    const pinsAfter = await page.locator('.maplibregl-marker .pin-inner').count()
    fs.writeFileSync(path.join(OUT_DIR, 'mapa-piny.json'), JSON.stringify({ pinsBefore, pinsAfter }, null, 2))
  })

  test('akcie-prazdny', async ({ page }) => {
    await setup(page, { period: { type: 'today' }, filter: { types: ['culture'], subtypes: ['quiz'], genres: [], characters: [], sizes: [], free: false } })
    await page.goto('/#/akcie')
    await page.waitForSelector('[data-testid="filter-empty"]:visible', { timeout: 15000 })
    await page.waitForTimeout(1500)
    await shot(page, 'akcie-prazdny.jpg')
  })
})
