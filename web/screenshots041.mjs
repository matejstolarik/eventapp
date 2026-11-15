import { chromium } from '@playwright/test'
import path from 'path'
import { mkdirSync } from 'fs'

const BASE = 'http://localhost:5174/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\041'
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
})
const page = await ctx.newPage()

await ctx.addInitScript(() => {
  localStorage.setItem('language', 'sk')
  localStorage.setItem('favorites', JSON.stringify(['cross-club', 'fuchs2']))
  localStorage.removeItem('eventsFilters')
  localStorage.setItem('eventsPeriod', JSON.stringify({ type: 'anytime' }))
})

async function goEvents(waitMs = 2500) {
  await page.goto(BASE)
  await page.waitForTimeout(waitMs)
  // Click the Events tab – active tab shows label text, inactive tabs only have icon + aria-label
  await page.evaluate(() => {
    const btns = document.querySelectorAll('button')
    for (const b of btns) {
      const label = b.getAttribute('aria-label')
      if (label === 'Akcie' || label === 'Events' || label === 'Akce') { b.click(); break }
    }
  })
  await page.waitForTimeout(600)
}

// 01 – Akcie mriežka: vypnuté čipy, viditeľné odznaky a ikony v plochách
await goEvents()
await page.screenshot({ path: path.join(OUT, '01-akcie-odznaky.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 01-akcie-odznaky.jpg')

// 02 – Pre teba: zapnutý čip
await goEvents()
await page.evaluate(() => {
  const btns = document.querySelectorAll('button')
  for (const b of btns) {
    if (b.textContent && b.textContent.trim().includes('Pre teba')) { b.click(); break }
  }
})
await page.waitForTimeout(400)
await page.screenshot({ path: path.join(OUT, '02-akcie-pre-teba.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 02-akcie-pre-teba.jpg')

// 03 – Hľadanie: napísané "techno"
await goEvents()
// Click search button
await page.evaluate(() => {
  const btns = document.querySelectorAll('button')
  for (const b of btns) {
    if (b.getAttribute('aria-label') === 'Hľadať') { b.click(); break }
  }
})
await page.waitForTimeout(300)
const inp = await page.$('input')
if (inp) {
  await inp.click()
  await inp.type('techno', { delay: 50 })
  await page.waitForTimeout(400)
}
await page.screenshot({ path: path.join(OUT, '03-hladanie.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 03-hladanie.jpg')

// 04 – Hľadanie nič: napísané niečo čo nič nenájde
await goEvents()
await page.evaluate(() => {
  const btns = document.querySelectorAll('button')
  for (const b of btns) {
    if (b.getAttribute('aria-label') === 'Hľadať') { b.click(); break }
  }
})
await page.waitForTimeout(300)
const inp2 = await page.$('input')
if (inp2) {
  await inp2.click()
  await inp2.type('xqzwkjhfplasmoid123', { delay: 50 })
  await page.waitForTimeout(400)
}
await page.screenshot({ path: path.join(OUT, '04-hladanie-nic.jpg'), type: 'jpeg', quality: 80 })
console.log('saved 04-hladanie-nic.jpg')

await browser.close()
console.log('All done.')
