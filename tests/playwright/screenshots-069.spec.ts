import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 069: row in Akcie, map card, venue programme and My account as before
// 068, event page, separators. Real events.json and images from GitHub Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/069')
fs.mkdirSync(OUT_DIR, { recursive: true })
const PICKS = JSON.parse(fs.readFileSync(path.resolve('D:/AI/eventapp/docs/tasks/068/picks.json'), 'utf-8'))
const NOW = '2026-11-18T19:30:00'

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

async function shot(page: any, name: string, clip?: any) {
  await page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80, scale: 'css', ...(clip ? { clip } : {}) })
}

test.describe('069', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie + meranie', async ({ page }) => {
    await setup(page, { favorites: PICKS.favorites })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await shot(page, 'akcie-dnes.jpg')
    // measure the text block of rows (title lines, meta line, tag row)
    const m = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('[role="button"]')).filter(r => (r as HTMLElement).style.height)
      return rows.slice(0, 40).map(r => {
        const block = r.children[1] as HTMLElement
        const [title, meta] = Array.from(block.children) as HTMLElement[]
        return { row: r.getBoundingClientRect().height, img: (r.children[0] as HTMLElement).getBoundingClientRect().width,
          block: block.getBoundingClientRect().height, title: title.getBoundingClientRect().height, meta: meta.getBoundingClientRect().height }
      })
    })
    fs.writeFileSync(path.join(OUT_DIR, 'meranie.json'), JSON.stringify(m))
    console.log('MEASURE', JSON.stringify(m.slice(0, 6)))
    // one-line and two-line titles next to each other
    const clip = await page.evaluate(() => {
      const rows = Array.from(document.querySelectorAll('[role="button"]')).filter(r => (r as HTMLElement).style.height) as HTMLElement[]
      const lines = (r: HTMLElement) => Math.round(((r.children[1] as HTMLElement).children[0] as HTMLElement).getBoundingClientRect().height / 17.5)
      for (let i = 0; i + 1 < rows.length; i++) {
        if (lines(rows[i]) !== lines(rows[i + 1])) {
          rows[i].scrollIntoView({ block: 'center' })
          return i
        }
      }
      return -1
    })
    await page.waitForTimeout(1500)
    if (clip >= 0) {
      const box = await page.evaluate((i: number) => {
        const rows = Array.from(document.querySelectorAll('[role="button"]')).filter(r => (r as HTMLElement).style.height) as HTMLElement[]
        const a = rows[i].getBoundingClientRect(), b = rows[i + 1].getBoundingClientRect()
        return { x: 0, y: Math.max(0, a.top - 12), width: 390, height: b.bottom - a.top + 24 }
      }, clip)
      await shot(page, 'akcie-jednoriadkovy-nazov.jpg', box)
    }
  })

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

  test('detail', async ({ page }) => {
    await setup(page)
    await page.goto(`/#/akcia/${PICKS.poster}`)
    await page.waitForSelector('text=Zdieľať', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await shot(page, 'detail.jpg')
  })

  test('miesta', async ({ page }) => {
    await setup(page, { favorites: PICKS.favorites })
    await page.goto('/#/miesta')
    await page.waitForTimeout(3000)
    await shot(page, 'miesta.jpg')
  })
})
