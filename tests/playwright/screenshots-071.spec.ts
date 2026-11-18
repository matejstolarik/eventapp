import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 071: culture subtype icons, no subtype tags in lists, type icon on the
// map card, tags always English. Real events.json and images from Pages.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/071')
fs.mkdirSync(OUT_DIR, { recursive: true })
const NOW = '2026-11-18T17:00:00'
const VENUE = 'archa-plus'
const ROW_TITLE = 'Uvedení hry'
const DETAIL = 'archa-plus-2026-11-18-burkicom-slunce'

async function setup(page: any, lang = 'sk') {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript((l: string) => {
    localStorage.setItem('language', l)
    localStorage.setItem('going', '[]')
    localStorage.setItem('favorites', '[]')
  }, lang)
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

test.describe('071', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  test('akcie-dnes', async ({ page }) => {
    await setup(page)
    await page.goto('/#/akcie')
    await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
    await page.waitForTimeout(2000)
    await page.getByText(ROW_TITLE).first().evaluate((el: HTMLElement) => el.scrollIntoView({ block: 'center' }))
    await page.waitForTimeout(2000)
    await shot(page, 'akcie-dnes.jpg')
  })

  test('mapa-karta', async ({ page }) => {
    await setup(page)
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2500)
    await page.evaluate((vid: string) => {
      (document.querySelector(`.map-pin[data-venue-id="${vid}"]`) as HTMLElement | null)?.click()
    }, VENUE)
    await page.waitForTimeout(2500)
    await shot(page, 'mapa-karta.jpg')
  })

  test('program-podniku', async ({ page }) => {
    await setup(page)
    await page.goto(`/#/miesto/${VENUE}`)
    await page.waitForSelector('text=Program', { timeout: 15000 })
    await page.waitForTimeout(1500)
    await page.getByText('Program', { exact: true }).first().scrollIntoViewIfNeeded()
    await page.mouse.move(195, 500)
    await page.mouse.wheel(0, 250)
    await page.waitForTimeout(2000)
    await shot(page, 'program-podniku.jpg')
  })

  test('detail-cs', async ({ page }) => {
    await setup(page, 'cs')
    await page.goto(`/#/akcia/${DETAIL}`)
    await page.waitForTimeout(3500)
    await shot(page, 'detail-cs.jpg')
  })
})

test.describe('071 icons 3x', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 3 })

  test('ikony-3x', async ({ page }) => {
    await setup(page)
    await page.goto('/#/ucet')
    await page.waitForTimeout(1500)
    await page.evaluate(async () => {
      const m = await import(/* @vite-ignore */ '/eventapp/src/map/markers.ts')
      const t = await import(/* @vite-ignore */ '/eventapp/src/core/eventType.ts')
      m.initPinShadows()
      const keys = ['concert', 'party', 'dj', 'film', 'standup', 'dance', 'culture', 'talk', 'workshop', 'quiz', 'opening']
      const typeOf = (k: string) => (k === 'concert' || k === 'party' || k === 'dj') ? k : 'culture'
      const box = document.createElement('div')
      box.id = 'icons071'
      box.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#111118;display:flex;flex-wrap:wrap;align-content:flex-start;gap:6px 4px;padding:10px'
      for (const k of keys) {
        const type = typeOf(k)
        const cell = document.createElement('div')
        cell.style.cssText = 'width:66px;height:118px;position:relative;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:6px'
        const pinWrap = document.createElement('div')
        pinWrap.style.cssText = 'position:relative;width:50px;height:70px'
        const pin = m.createPinElement({ venueId: k, name: '', eventType: type, iconKey: k, isFavorite: false, isLive: false, extraCount: 0, lat: 0, lng: 0 }, false)
        pin.style.position = 'absolute'; pin.style.left = '0'; pin.style.top = '0'
        pinWrap.appendChild(pin)
        const pill = document.createElement('span')
        pill.style.cssText = 'height:20px;padding:0 6px;border-radius:10px;background:#2A2838;display:inline-flex;align-items:center'
        pill.innerHTML = m.typeIconSvg(k, t.EVENT_TYPE_TAG_TEXT[type], 13, '#2A2838')
        const label = document.createElement('span')
        label.textContent = k
        label.style.cssText = 'font:500 9px sans-serif;color:#8E8AA6'
        cell.append(pinWrap, pill, label)
        box.appendChild(cell)
      }
      document.body.appendChild(box)
    })
    await page.waitForTimeout(500)
    await page.screenshot({ path: path.join(OUT_DIR, 'ikony-3x.png'), clip: { x: 0, y: 0, width: 390, height: 400 } })
  })
})
