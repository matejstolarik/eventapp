import { chromium } from '@playwright/test'
import path from 'path'

const BASE = 'http://localhost:5175/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\033'

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
  locale: 'sk-SK',
})
const page = await ctx.newPage()

await ctx.addInitScript(() => { localStorage.setItem('language', 'sk') })

async function go(hash, file, waitMs = 2000) {
  await page.goto(BASE + hash)
  await page.waitForTimeout(waitMs)
  await page.screenshot({ path: path.join(OUT, file), fullPage: false })
  console.log('saved', file)
}

// 1. Map — zoom 13 showing centered pin names
await page.goto(BASE)
await page.waitForTimeout(3000)
// Zoom in by double-clicking
await page.mouse.dblclick(195, 422)
await page.waitForTimeout(1000)
await page.mouse.dblclick(195, 422)
await page.waitForTimeout(1000)
await page.mouse.dblclick(195, 422)
await page.waitForTimeout(1500)
await page.screenshot({ path: path.join(OUT, '01-mapa-mena-pinov.png'), fullPage: false })
console.log('saved 01-mapa-mena-pinov.png')

// 2. Places — Všetky miesta
await go('#/miesta', '02-miesta-vsetky.png', 2000)

// 3. Places — Obľúbené toggle (click via JS evaluate)
await page.goto(BASE + '#/miesta')
await page.waitForTimeout(1500)
await page.evaluate(() => {
  const groups = document.querySelectorAll('[role="group"]')
  for (const g of groups) {
    const btns = g.querySelectorAll('button')
    if (btns.length === 2) { btns[1].click(); break }
  }
})
await page.waitForTimeout(500)
await page.screenshot({ path: path.join(OUT, '03-miesta-oblubene.png'), fullPage: false })
console.log('saved 03-miesta-oblubene.png')

// 4. Venue profile — Cross Club (action buttons)
await go('#/miesto/cross-club', '04-venue-cross-club.png', 1500)

// 5. Venue profile — Roxy (another venue)
await go('#/miesto/roxy', '05-venue-roxy.png', 1500)

await browser.close()
console.log('Done')
