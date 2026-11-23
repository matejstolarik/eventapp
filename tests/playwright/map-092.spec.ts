import { test, expect, type Page } from '@playwright/test'

// Task 092: (6) map after a lost WebGL context is drawn again (not black), pins and
// panel stay; (7) "Na mape" from the event page always centres the map on the venue.
// Local dev server, real events.json from Pages.  Reads the map through window.__map
// (dev only).
const PAGES = 'https://matejstolarik.github.io/eventapp/'

type Ev = { id: string; venue_id: string; date: string }
type Vn = { id: string; lat: number; lng: number; name: string }
let DATA: { events: Ev[]; venues: Vn[] } | null = null

async function setup(page: Page) {
  await page.addInitScript(() => {
    if (!sessionStorage.getItem('init092')) {
      localStorage.clear()
      localStorage.setItem('language', 'sk')
      localStorage.setItem('onboardingDone', '1')
      sessionStorage.setItem('init092', '1')
    }
  })
  await page.route('**/events.json', async (route: any) => {
    const resp = await route.fetch({ url: PAGES + 'events.json' })
    if (!DATA) DATA = JSON.parse(await resp.text())
    await route.fulfill({ response: resp })
  })
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* test ended */ }
  })
}

async function openMap(page: Page) {
  await page.goto('#/mapa')
  await page.waitForFunction(() => {
    const m = (window as any).__map
    return m && m.loaded() && m.isStyleLoaded() && m.areTilesLoaded()
  }, null, { timeout: 30000 })
  await page.waitForSelector('.map-pin', { timeout: 15000 })
  await page.waitForTimeout(1200)
}

/** Share of non-dark pixels of the map canvas, read right after a render. */
async function litShare(page: Page): Promise<number> {
  return page.evaluate(() => new Promise<number>(resolve => {
    const map = (window as any).__map
    const done = () => {
      const src = map.getCanvas() as HTMLCanvasElement
      const c = document.createElement('canvas')
      c.width = 60; c.height = 60
      const ctx = c.getContext('2d')!
      ctx.drawImage(src, 0, 0, 60, 60)
      const d = ctx.getImageData(0, 0, 60, 60).data
      let lit = 0
      for (let i = 0; i < d.length; i += 4) if (d[i]! + d[i + 1]! + d[i + 2]! > 60) lit++
      resolve(lit / 3600)
    }
    map.once('render', done)
    map.triggerRepaint()
    setTimeout(() => resolve(-1), 5000)
  }))
}

async function setVisibility(page: Page, state: 'hidden' | 'visible') {
  await page.evaluate((state) => {
    Object.defineProperty(document, 'visibilityState', { value: state, configurable: true })
    Object.defineProperty(document, 'hidden', { value: state === 'hidden', configurable: true })
    document.dispatchEvent(new Event('visibilitychange'))
  }, state)
}

async function selectFirstPin(page: Page) {
  const pin = page.locator('.map-pin').first()
  const vid = await pin.getAttribute('data-venue-id')
  await pin.click()
  await page.waitForTimeout(800)
  return vid
}

test.describe('092 map', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

  for (const restore of [true, false]) {
    test(`lost WebGL context${restore ? ' restored' : ' not restored'} → map drawn again`, async ({ page }) => {
      test.setTimeout(90000)
      await setup(page)
      await openMap(page)
      const vid = await selectFirstPin(page)
      const before = await litShare(page)
      const view = await page.evaluate(() => { const m = (window as any).__map; return { c: m.getCenter(), z: m.getZoom() } })
      console.log('lit before', before)
      expect(before).toBeGreaterThan(0.5)

      // the same pin elements must survive (no new appear animation)
      await page.evaluate(() => { (document.querySelector('.map-pin') as HTMLElement).dataset.keep = '1' })
      await setVisibility(page, 'hidden')
      await page.evaluate(() => {
        const gl = (window as any).__map.painter.context.gl as WebGLRenderingContext
        ;(window as any).__loseExt = gl.getExtension('WEBGL_lose_context')
        ;(window as any).__loseExt.loseContext()
      })
      await page.waitForTimeout(500)
      if (restore) await page.evaluate(() => (window as any).__loseExt.restoreContext())
      await page.waitForTimeout(300)
      await setVisibility(page, 'visible')
      await page.waitForFunction(() => {
        const m = (window as any).__map
        return m && m.loaded() && m.areTilesLoaded() && !m.painter.context.gl.isContextLost()
      }, null, { timeout: 20000 })
      await page.waitForTimeout(1500)
      const after = await litShare(page)
      console.log('lit after', after)
      expect(after).toBeGreaterThan(0.5)
      const view2 = await page.evaluate(() => { const m = (window as any).__map; return { c: m.getCenter(), z: m.getZoom() } })
      expect(Math.abs(view2.z - view.z)).toBeLessThan(0.01)
      expect(Math.abs(view2.c.lng - view.c.lng)).toBeLessThan(1e-4)
      await expect(page.locator('.map-pin').first()).toBeVisible()
      await expect(page.locator(`.map-pin.pin-selected[data-venue-id="${vid}"]`)).toHaveCount(1)
      await expect(page.locator('[data-testid="event-panel"]')).toBeVisible()
      await expect(page.locator('.map-pin[data-keep="1"]')).toHaveCount(1)
    })
  }

  // from: 'map' = event opened over the map; 'events' = from the Akcie tab after the map
  // was opened and moved; 'cold' = Akcie tab, map never shown since the app started
  for (const from of ['map', 'events', 'cold'] as const) for (const otherDay of [false, true]) {
    test(`"Na mape" centres the venue (from ${from}, ${otherDay ? 'other day' : 'selected day'})`, async ({ page }) => {
      test.setTimeout(90000)
      await setup(page)
      if (from === 'cold') {
        await page.goto('')
        await page.waitForSelector('text=Zoradiť', { timeout: 20000 })
        await page.waitForFunction(() => (window as any).__map?.loaded(), null, { timeout: 30000 })
      } else {
        await openMap(page)
        // move the map far away from the venue first
        await page.evaluate(() => (window as any).__map.jumpTo({ center: [14.30, 50.03], zoom: 13.5 }))
        await page.waitForTimeout(500)
        if (from === 'events') {
          await page.locator('nav button[aria-label="Akcie"]').click()
          await page.waitForTimeout(500)
        }
      }
      const today = await page.evaluate(() => {
        const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      })
      const ev = (otherDay ? DATA!.events.find(e => e.date > today && e.venue_id !== 'cross-club')
        : DATA!.events.find(e => e.date === today && e.venue_id !== 'cross-club'))
        ?? DATA!.events.find(e => e.date > today)!
      const venue = DATA!.venues.find(v => v.id === ev.venue_id)!
      console.log('event', ev.id, ev.date, venue.id)
      await page.evaluate((id) => { window.location.hash = `/akcia/${id}` }, ev.id)
      await page.getByRole('button', { name: 'Na mape' }).click()
      await page.waitForTimeout(2500)
      const r = await page.evaluate(([lng, lat]) => {
        const m = (window as any).__map
        const p = m.project([lng, lat])
        const cv = m.getCanvas().getBoundingClientRect()
        return { x: p.x, y: p.y, w: cv.width, h: cv.height }
      }, [venue.lng, venue.lat])
      const expX = r.w / 2, expY = 100 + (r.h - 100 - 240) / 2
      console.log(from, otherDay, 'venue at', r, 'expected', expX, expY)
      await expect(page.locator(`.map-pin.pin-selected[data-venue-id="${venue.id}"]`)).toHaveCount(1)
      await expect(page.locator('[data-testid="event-panel"]')).toBeVisible()
      expect(Math.abs(r.x - expX)).toBeLessThan(8)
      expect(Math.abs(r.y - expY)).toBeLessThan(8)
    })
  }
})
