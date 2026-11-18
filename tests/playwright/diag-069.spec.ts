import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 069 part 1: what happens on screen right after tapping an event in Akcie.
// Real data from GitHub Pages; image downloads slowed down (Fast-3G-like delay)
// so a late image is visible. PHASE=pred|po picks the file name suffix.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/069')
const PHASE = process.env.PHASE ?? 'pred'
const NOW = '2026-11-18T19:30:00'
const IMG_DELAY = 900

test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })

test('diag open event', async ({ page }) => {
  await page.clock.setFixedTime(NOW)
  await page.addInitScript(() => { localStorage.setItem('language', 'sk') })
  await page.route('**/events.json', async (route: any) =>
    route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    const resp = await route.fetch({ url: PAGES + rel })
    if (rel.includes('detail')) await new Promise(r => setTimeout(r, IMG_DELAY))
    route.fulfill({ response: resp })
  })
  await page.goto('/#/akcie')
  await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
  await page.waitForTimeout(2500)
  // scroll the list a bit, like a user would
  await page.mouse.move(195, 500)
  await page.mouse.wheel(0, 600)
  await page.waitForTimeout(1200)
  // log the y of the event page title every frame
  await page.evaluate(() => {
    const w = window as any
    w.__log = []
    const t0 = performance.now()
    const tick = () => {
      // event page overlay = fixed div with z-index 50; title = its h1
      const ovs = Array.from(document.querySelectorAll('div')).filter(d => d.style.zIndex === '50' && d.style.overflowY === 'auto')
      const ov = ovs[0] as HTMLElement | undefined
      const h = ov?.querySelector('h1') as HTMLElement | null
      const img = ov?.querySelector('img') as HTMLImageElement | null
      w.__log.push([Math.round(performance.now() - t0), h ? Math.round(h.getBoundingClientRect().top) : null, ov ? ov.scrollTop : null, img ? img.getBoundingClientRect().height : null])
      if (performance.now() - t0 < 2500) requestAnimationFrame(tick)
    }
    w.__t0 = t0
    requestAnimationFrame(tick)
  })
  const rows = page.locator('[role="button"]')
  await rows.nth(3).click()
  const start = Date.now()
  for (const ms of [0, 100, 300, 800]) {
    const wait = ms - (Date.now() - start)
    if (wait > 0) await page.waitForTimeout(wait)
    await page.screenshot({ path: path.join(OUT_DIR, `diag-${PHASE}-${ms}ms.jpg`), type: 'jpeg', quality: 80 })
  }
  await page.waitForTimeout(1500)
  const log = await page.evaluate(() => (window as any).__log as number[][])
  // keep only frames where something changed
  const changes = log.filter((r, i) => i === 0 || r[1] !== log[i - 1][1] || r[2] !== log[i - 1][2] || r[3] !== log[i - 1][3])
  fs.writeFileSync(path.join(OUT_DIR, `diag-${PHASE}-log.json`), JSON.stringify(changes))
  console.log('DIAG', PHASE, JSON.stringify(changes))
})
