import { chromium } from '@playwright/test'
import path from 'path'
import { mkdirSync } from 'fs'

const BASE = 'http://localhost:5174/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\044'
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
})
const page = await ctx.newPage()

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

async function goEvents(period = 'anytime') {
  // Navigate first to get correct origin, then set localStorage
  await page.goto(BASE)
  await sleep(500)
  await page.evaluate((p) => {
    localStorage.setItem('language', 'sk')
    localStorage.setItem('favorites', JSON.stringify(['cross-club', 'fuchs2']))
    localStorage.removeItem('eventsFilters')
    localStorage.setItem('eventsPeriod', JSON.stringify({ type: p }))
  }, period)
  await page.reload()
  await sleep(2500)
  // Click Events tab
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button')
    for (const b of btns) {
      const label = b.getAttribute('aria-label')
      if (label === 'Akcie' || label === 'Events') { b.click(); break }
    }
  })
  await sleep(600)
}

async function scrollPageDown() {
  await page.evaluate(() => {
    const scrollables = Array.from(document.querySelectorAll('*'))
    for (const s of scrollables) {
      const style = getComputedStyle(s)
      if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
          s.scrollHeight > s.clientHeight + 100 &&
          s !== document.body && s !== document.documentElement) {
        s.scrollTop = 1000
        return
      }
    }
    window.scrollTo(0, 1000)
  })
}

// 01 – Akcie Kedykolvek: full header, no count row
await goEvents('anytime')
await page.screenshot({ path: path.join(OUT, '01-akcie-kedykolvek.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 01-akcie-kedykolvek.jpg')

// 02 – Akcie zbalene: compact bar visible after scrolling
await goEvents('next7')
await scrollPageDown()
await sleep(600)
await page.screenshot({ path: path.join(OUT, '02-akcie-zbalene.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 02-akcie-zbalene.jpg')

// 03 – Miesta sipka navrch
await page.goto(BASE)
await sleep(500)
await page.evaluate(() => { localStorage.setItem('language', 'sk') })
await page.reload()
await sleep(2500)
await page.evaluate(() => {
  const btns = document.querySelectorAll('button')
  for (const b of btns) {
    if (b.getAttribute('aria-label') === 'Miesta' || b.getAttribute('aria-label') === 'Places') { b.click(); break }
  }
})
await sleep(600)
await scrollPageDown()
await sleep(600)
await page.screenshot({ path: path.join(OUT, '03-miesta-sipka.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 03-miesta-sipka.jpg')

// 04 – Akcie stitky na obrazku
await goEvents('anytime')
await page.screenshot({ path: path.join(OUT, '04-akcie-stitky-na-obrazku.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 04-akcie-stitky-na-obrazku.jpg')

await browser.close()
console.log('All done.')
