import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 068: row A3, map card, event page with the whole image.
// Real events.json and images from GitHub Pages (latest pipeline run).
// Event ids for the detail shots come from docs/tasks/068/picks.json.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/068')
fs.mkdirSync(OUT_DIR, { recursive: true })
const PICKS = JSON.parse(fs.readFileSync(path.join(OUT_DIR, 'picks.json'), 'utf-8'))
const NOW = '2026-11-18T18:00:00'

async function setup(page: any, opts: { going?: string[]; favorites?: string[] } = {}) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript((o: any) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('going', JSON.stringify(o.going ?? []))
    localStorage.setItem('favorites', JSON.stringify(o.favorites ?? []))
  }, opts)
  await page.route('**/events.json', async (route: any) =>
    route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    route.fulfill({ response: await route.fetch({ url: PAGES + rel }) })
  })
}

async function shot(page: any, name: string) {
  await page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80 })
}

async function tab(page: any, idx: number) {
  await page.evaluate((i: number) => {
    const tabs = Array.from(document.querySelectorAll('button')).filter(b => {
      const r = b.getBoundingClientRect(); return r.top > 700 && r.bottom > 740
    }) as HTMLButtonElement[]
    tabs[i]?.click()
  }, idx)
}

test.describe('068', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie', async ({ page }) => {
    await setup(page, { favorites: PICKS.favorites })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await shot(page, 'akcie-dnes.jpg')
    await page.mouse.move(195, 500)
    await page.mouse.wheel(0, 900)
    await page.waitForTimeout(1500)
    await shot(page, 'akcie-scroll.jpg')
  })

  if (PICKS.noImage) {
    test('akcia-bez-obrazka', async ({ page }) => {
      await setup(page)
      await page.goto('/#/akcie')
      await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
      await page.waitForTimeout(1500)
      // the event is today: scroll its row into the middle of the list
      await page.getByText(PICKS.noImage.title, { exact: true }).first().evaluate((el: Element) => el.scrollIntoView({ block: 'center' }))
      await page.waitForTimeout(2000)
      await shot(page, 'akcia-bez-obrazka.jpg')
    })
  }

  test('mapa-karta', async ({ page }) => {
    await setup(page, { favorites: PICKS.favorites })
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await page.evaluate((vid: string) => {
      const el = document.querySelector(`.map-pin[data-venue-id="${vid}"]`) as HTMLElement | null
      ;(el ?? document.querySelector('.map-pin') as HTMLElement | null)?.click()
    }, PICKS.mapVenue)
    await page.waitForTimeout(2500)
    await shot(page, 'mapa-karta.jpg')
  })

  test('program-podniku', async ({ page }) => {
    await setup(page)
    await page.goto(`/#/miesto/${PICKS.programVenue}`)
    await page.waitForSelector('text=Program', { timeout: 15000 })
    await page.waitForTimeout(1500)
    await page.getByText('Program', { exact: true }).first().scrollIntoViewIfNeeded()
    await page.mouse.move(195, 500)
    await page.mouse.wheel(0, 250)
    await page.waitForTimeout(2000)
    await shot(page, 'program-podniku.jpg')
  })

  test('moje-akcie', async ({ page }) => {
    await setup(page, { going: PICKS.going })
    await page.goto('/#/ucet')
    await page.waitForTimeout(3500)
    await shot(page, 'moje-akcie.jpg')
  })

  for (const [name, key] of [['detail-banner.jpg', 'banner'], ['detail-plagat.jpg', 'poster'], ['detail-bez-stitkov.jpg', 'noTags']] as const) {
    if (!PICKS[key]) continue
    test(name, async ({ page }) => {
      await setup(page)
      await page.goto(`/#/akcia/${PICKS[key]}`)
      await page.waitForSelector('text=Zdieľať', { timeout: 15000 })
      await page.waitForTimeout(2500)
      await shot(page, name)
    })
  }
})
