import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 072: max 4 pills without fade, language order, date in Môj účet,
// full-width cropped detail image, zoomable poster. Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/072')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-19T17:00:00'
const PORTRAIT = 'meetfactory-2026-11-21-good-times-only-krest-desky-blue-uandi'
const LANDSCAPE = 'cross-club-2026-11-20-moordoor'
const GOING = [PORTRAIT, LANDSCAPE, 'cross-club-2026-11-30-los-tekkenos']

async function setup(page: any, going: string[] = []) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript((g: string[]) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('going', JSON.stringify(g))
    localStorage.setItem('favorites', '[]')
  }, going)
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

test.describe('072', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie-dnes', async ({ page }) => {
    await setup(page)
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(3000)
    await shot(page, 'akcie-dnes.jpg')
  })

  test('detail-plagat-na-vysku', async ({ page }) => {
    await setup(page)
    await page.goto(`/#/akcia/${PORTRAIT}`)
    await page.waitForTimeout(3500)
    // full width, height = 50 % of the screen
    const box = await page.locator('img').first().boundingBox()
    console.log('portrait hero', JSON.stringify(box))
    expect(Math.round(box!.width)).toBe(390)
    expect(Math.round(box!.height)).toBe(422)
    await shot(page, 'detail-plagat-na-vysku.jpg')
  })

  test('detail-na-sirku', async ({ page }) => {
    await setup(page)
    await page.goto(`/#/akcia/${LANDSCAPE}`)
    await page.waitForTimeout(3500)
    const box = await page.locator('img').first().boundingBox()
    console.log('landscape hero', JSON.stringify(box))
    expect(Math.round(box!.width)).toBe(390)
    await shot(page, 'detail-na-sirku.jpg')
  })

  test('moj-ucet', async ({ page }) => {
    await setup(page, GOING)
    await page.goto('/#/ucet')
    await page.waitForTimeout(3000)
    await shot(page, 'moj-ucet-akcie.jpg')
    await page.mouse.move(195, 500)
    await page.mouse.wheel(0, 2000)
    await page.waitForTimeout(800)
    await shot(page, 'moj-ucet-jazyk.jpg')
  })

  test('plagat-zoom', async ({ page }) => {
    await setup(page)
    await page.goto(`/#/akcia/${PORTRAIT}`)
    await page.waitForTimeout(3000)
    await page.getByRole('button', { name: 'Plagát' }).click()
    await page.waitForTimeout(2500)
    // a single tap must not close the overlay any more
    await page.mouse.click(195, 300)
    await page.waitForTimeout(600)
    await page.mouse.dblclick(195, 300)
    await page.waitForTimeout(800)
    const tf = await page.locator('div[style*="z-index: 200"] img').evaluate((el: HTMLElement) => el.style.transform)
    console.log('poster transform', tf)
    expect(tf).toContain('scale(2.5)')
    await shot(page, 'plagat-zoom.jpg')
  })
})
