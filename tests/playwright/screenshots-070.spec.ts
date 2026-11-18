import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 070: type icon pill in the Akcie row and venue programme, for-you
// sparkles on the image, 120 x 90 row image. Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/070')
fs.mkdirSync(OUT_DIR, { recursive: true })
const PICKS = JSON.parse(fs.readFileSync(path.resolve('D:/AI/eventapp/docs/tasks/068/picks.json'), 'utf-8'))
const NOW = '2026-11-18T19:30:00'

async function setup(page: any, opts: { favorites?: string[] } = {}) {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript((o: any) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('going', '[]')
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
  await page.screenshot({ path: path.join(OUT_DIR, name), type: 'jpeg', quality: 80, scale: 'css' })
}

test.describe('070', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie-dnes', async ({ page }) => {
    await setup(page, { favorites: PICKS.favorites })
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await shot(page, 'akcie-dnes.jpg')
    const m = await page.evaluate(() => {
      const r = Array.from(document.querySelectorAll('[role="button"]')).find(r => (r as HTMLElement).style.height) as HTMLElement
      const img = r.children[0].getBoundingClientRect()
      return { row: r.getBoundingClientRect().height, imgW: img.width, imgH: img.height, block: r.children[1].getBoundingClientRect().height }
    })
    console.log('MEASURE', JSON.stringify(m))
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
})

test.describe('070 sparkles 3x', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3 })

  test('iskry-3x', async ({ page }) => {
    // every venue a favourite -> every row has the for-you sparkles
    const data = await (await fetch(PAGES + 'events.json')).json()
    const venues = [...new Set((data.events as any[]).map(e => e.venue_id))]
    await setup(page, { favorites: venues })
    await page.addInitScript(() => localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'next7' })))
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(3000)
    // load more lazy images: scroll the list down in steps
    // load the lazy row images up front (first 60 rows)
    await page.evaluate(() => Array.from(document.querySelectorAll('[role="button"] img')).slice(0, 60)
      .forEach(i => { (i as HTMLImageElement).loading = 'eager' }))
    await page.waitForTimeout(5000)
    // brightness of the top-left 30x30 px of each loaded row image
    const lum = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('[role="button"] img')) as HTMLImageElement[]
      const c = document.createElement('canvas'); c.width = 30; c.height = 30
      const g = c.getContext('2d')!
      return imgs.slice(0, 60).map((img, i) => {
        if (!img.complete || !img.naturalWidth) return [i, -1]
        const r = img.getBoundingClientRect()
        g.drawImage(img, 0, 0, img.naturalWidth * 30 / r.width, img.naturalHeight * 30 / r.height, 0, 0, 30, 30)
        const d = g.getImageData(0, 0, 30, 30).data
        let s = 0
        for (let k = 0; k < d.length; k += 4) s += 0.2126 * d[k] + 0.7152 * d[k + 1] + 0.0722 * d[k + 2]
        return [i, s / (d.length / 4)]
      }).filter(x => x[1] >= 0)
    })
    lum.sort((a: any, b: any) => a[1] - b[1])
    const picks: [string, number][] = [['tmavy', lum[0][0]], ['svetly', lum[lum.length - 1][0]]]
    console.log('LUM', JSON.stringify([lum[0], lum[lum.length - 1]]))
    for (const [name, idx] of picks) {
      const box = await page.evaluate((i: number) => {
        const img = (document.querySelectorAll('[role="button"] img')[i] as HTMLElement)
        img.scrollIntoView({ block: 'center' })
        const r = img.parentElement!.getBoundingClientRect()
        return { x: r.left, y: r.top, width: 40, height: 34 }
      }, idx)
      await page.waitForTimeout(300)
      await page.screenshot({ path: path.join(OUT_DIR, `iskry-3x-${name}.png`), clip: box })
    }
  })
})
