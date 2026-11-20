import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 081: smoothness before / after the animations. Chromium, CPU throttled 4x
// (CDP Emulation.setCPUThrottlingRate), 390 x 844, real events.json from Pages.
// Production builds: BEFORE_URL (commit before 081) and AFTER_URL (this commit),
// served by `vite preview`. Per scenario: frames from requestAnimationFrame in
// the 700 ms after the tap (avg / worst FPS, longest frame) and the time from the
// tap (pointerdown) to the first frame after the content is in the DOM.
const PAGES = 'https://matejstolarik.github.io/eventapp/'
const OUT = path.resolve('D:/AI/eventapp/docs/tasks/081/perf.json')
const RUNS = Number(process.env.PERF_RUNS ?? 3)
const VERSIONS: Record<string, string> = {
  before: process.env.BEFORE_URL ?? 'http://localhost:4180/eventapp/',
  after: process.env.AFTER_URL ?? 'http://localhost:4181/eventapp/',
}

type Result = { avgFps: number; worstFps: number; longestFrame: number; toContent: number | null }

async function setup(page: any, favorites: string[]) {
  await page.addInitScript((favs: string[]) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('onboardingDone', '1')
    localStorage.setItem('favorites', JSON.stringify(favs))
    localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'next7' }))
    localStorage.setItem('locationAsked', '1')
  }, favorites)
  await page.context().grantPermissions([])
  await page.route('**/events.json', async (route: any) => {
    await route.fulfill({ response: await route.fetch({ url: PAGES + 'events.json' }) })
  })
  await page.route(/\/eventapp\/img\//, async (route: any) => {
    const rel = route.request().url().split('/eventapp/')[1]
    try { await route.fulfill({ response: await route.fetch({ url: PAGES + rel }) }) } catch { /* ended */ }
  })
}

/** Starts frame + content recording; `pred` is JS source of a () => boolean. */
async function arm(page: any, pred: string) {
  await page.evaluate((predSrc: string) => {
    const check = new Function(`return (${predSrc})()`) as () => boolean
    const st: any = { t0: null, t1: null, seen: false, frames: [] as number[] }
    ;(window as any).__st = st
    document.addEventListener('pointerdown', () => { if (st.t0 == null) st.t0 = performance.now() }, { capture: true, once: true })
    const loop = (t: number) => {
      st.frames.push(t)
      if (st.seen && st.t1 == null) st.t1 = performance.now()
      if (st.t0 == null || t - st.t0 < 900) requestAnimationFrame(loop)
    }
    requestAnimationFrame(loop)
    st.mo = new MutationObserver(() => { if (st.t0 != null && !st.seen && check()) st.seen = true })
    st.mo.observe(document.body, { subtree: true, childList: true, attributes: true, characterData: true })
  }, pred)
}

async function collect(page: any): Promise<Result> {
  await page.waitForTimeout(1300)
  return page.evaluate(() => {
    const st = (window as any).__st
    st.mo.disconnect()
    const fr = (st.frames as number[]).filter(t => t >= st.t0 && t <= st.t0 + 700)
    const deltas = fr.slice(1).map((t, i) => t - fr[i]!)
    const longest = deltas.length ? Math.max(...deltas) : 0
    const span = fr.length > 1 ? fr[fr.length - 1]! - fr[0]! : 0
    return {
      avgFps: span ? Math.round(((fr.length - 1) / span) * 1000 * 10) / 10 : 0,
      worstFps: longest ? Math.round((1000 / longest) * 10) / 10 : 0,
      longestFrame: Math.round(longest * 10) / 10,
      toContent: st.t1 != null ? Math.round((st.t1 - st.t0) * 10) / 10 : null,
    }
  })
}

async function throttle(page: any, rate: number) {
  const cdp = await page.context().newCDPSession(page)
  await cdp.send('Emulation.setCPUThrottlingRate', { rate })
  return cdp
}

test.describe('081 perf', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, serviceWorkers: 'block', actionTimeout: 15000 })
  test.setTimeout(600_000)

  test('measure', async ({ page, request }) => {
    const data = await (await request.get(PAGES + 'events.json')).json()
    // favourites: venues with the most events (Pre teba has content)
    const byVenue = new Map<string, number>()
    for (const e of data.events) byVenue.set(e.venue_id, (byVenue.get(e.venue_id) ?? 0) + 1)
    const favs = [...byVenue.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([id]) => id)
    await setup(page, favs)

    const out: Record<string, Record<string, Result[]>> = {}
    for (const [ver, base] of Object.entries(VERSIONS)) {
      out[ver] = { period: [], forYou: [], tabMap: [], mapDay: [], heart: [] }
      for (let run = 0; run < RUNS; run++) {
        await page.goto(base + '#/akcie')
        await page.waitForSelector('text=Zoradiť', { timeout: 30000 })
        await page.waitForTimeout(2500)
        const cdp = await throttle(page, 4)

        // (a) period panel
        await arm(page, `() => Array.from(document.body.children).some(c => (c.textContent || '').startsWith('Obdobie'))`)
        await page.getByRole('button', { name: '7 dní', exact: true }).last().click()
        out[ver].period.push(await collect(page))
        await page.mouse.click(195, 100) // backdrop closes
        await page.waitForTimeout(800)

        // (b) Pre teba on
        await arm(page, `() => /\\d+ akci\\S* pre teba/.test(document.body.textContent || '')`)
        await page.getByRole('button', { name: 'Pre teba', exact: true }).last().click()
        out[ver].forYou.push(await collect(page))
        await page.getByRole('button', { name: 'Pre teba', exact: true }).last().click()
        await page.waitForTimeout(800)

        // (c) Akcie -> Mapa
        await arm(page, `() => document.querySelectorAll('.maplibregl-marker').length > 0`)
        await page.locator('nav button[aria-label="Mapa"]').click()
        out[ver].tabMap.push(await collect(page))
        await page.waitForSelector('.maplibregl-marker', { state: 'attached', timeout: 60000 })
        await page.waitForTimeout(2500)

        // (d) day change on the map (Dnes -> Zajtra)
        await page.locator('button[aria-label="Výber dňa"]').click()
        await page.waitForTimeout(800)
        await arm(page, `() => (document.querySelector('button[aria-label="Výber dňa"]')?.textContent || '').includes('Zajtra')`)
        await page.locator('button', { hasText: 'Zajtra' }).last().click()
        out[ver].mapDay.push(await collect(page))
        await page.waitForTimeout(800)

        // (e) heart in Miesta
        await page.locator('nav button[aria-label="Miesta"]').click()
        await page.waitForTimeout(1500)
        await page.evaluate(() => { document.querySelector('button[aria-label="Pridať do obľúbených"]')?.setAttribute('data-perf', '1') })
        await arm(page, `() => document.querySelector('[data-perf]')?.getAttribute('aria-label') === 'Odobrať z obľúbených'`)
        await page.locator('[data-perf]').click()
        out[ver].heart.push(await collect(page))

        await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 })
        await page.evaluate((f: string[]) => localStorage.setItem('favorites', JSON.stringify(f)), favs)
      }
    }
    fs.mkdirSync(path.dirname(OUT), { recursive: true })
    fs.writeFileSync(OUT, JSON.stringify({ runs: RUNS, cpuThrottle: 4, viewport: '390x844', favorites: favs, results: out }, null, 2))
    for (const [ver, sc] of Object.entries(out)) {
      for (const [name, rs] of Object.entries(sc)) {
        const avg = (k: keyof Result) => Math.round(rs.reduce((s, r) => s + ((r[k] as number) ?? 0), 0) / rs.length * 10) / 10
        console.log(`${ver.padEnd(6)} ${name.padEnd(7)} avgFps=${avg('avgFps')} worstFps=${Math.min(...rs.map(r => r.worstFps))} longest=${Math.max(...rs.map(r => r.longestFrame))}ms toContent=${avg('toContent')}ms`)
      }
    }
  })
})
