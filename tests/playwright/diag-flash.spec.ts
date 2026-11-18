import { test } from '@playwright/test'
const PAGES = 'https://matejstolarik.github.io/eventapp/'
test('flash', async ({ page }) => {
  await page.clock.setFixedTime('2026-11-18T17:00:00')
  await page.addInitScript(() => { localStorage.setItem('language', 'sk') })
  await page.route('**/events.json', async (r: any) => r.fulfill({ response: await r.fetch({ url: PAGES + 'events.json' }) }))
  await page.route(/\/eventapp\/img\//, async (r: any) => {
    const rel = r.request().url().split('/eventapp/')[1]; r.fulfill({ response: await r.fetch({ url: PAGES + rel }) })
  })
  await page.goto('/#/akcie')
  await page.waitForSelector('text=Zoradiť', { timeout: 15000 })
  await page.waitForTimeout(2500)
  for (const idx of [0, 3]) {
    await page.evaluate(() => {
      const log: any[] = []; (window as any).__log = log
      const t0 = performance.now()
      const probe = () => {
        const pts = [[195, 60], [195, 200], [195, 450], [195, 750]].map(([x, y]) => {
          let el = document.elementFromPoint(x, y) as HTMLElement | null
          let bg = ''
          for (let e = el; e && !bg; e = e.parentElement) { const c = getComputedStyle(e).backgroundColor; if (c !== 'rgba(0, 0, 0, 0)') bg = c }
          return (el?.tagName ?? '-') + ':' + bg + (el?.tagName === 'IMG' ? ':' + ((el as HTMLImageElement).complete ? 'ok' : 'loading') : '')
        })
        log.push([Math.round(performance.now() - t0), location.hash.slice(0, 20), ...pts])
        if (log.length < 25) requestAnimationFrame(probe)
      }
      requestAnimationFrame(probe)
    })
    await page.locator('[role="button"]').nth(idx).click()
    await page.waitForTimeout(1200)
    console.log(JSON.stringify(await page.evaluate(() => (window as any).__log), null, 0).replace(/\],\[/g, ']\n['))
    await page.goBack(); await page.waitForTimeout(1500)
  }
})
