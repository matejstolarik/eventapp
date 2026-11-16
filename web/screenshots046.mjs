import { chromium } from '@playwright/test'
import path from 'path'
import { mkdirSync } from 'fs'

const BASE = 'http://localhost:5174/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\046'
mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ headless: true })
const ctx = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 2,
})
const page = await ctx.newPage()

function sleep(ms) { return new Promise(r => setTimeout(r, ms)) }

// Get a valid event ID with start_time
await page.goto(BASE)
await sleep(600)
await page.evaluate(() => { localStorage.setItem('language', 'sk') })
await page.reload()
await sleep(2500)

const eventId = await page.evaluate(async () => {
  const r = await fetch('/eventapp/events.json')
  const d = await r.json()
  const ev = d.events.find(e => e.start_time)
  return ev?.id
})
console.log('eventId:', eventId)

// --- Screenshot 1: event page, Idem off ---
await page.evaluate((id) => {
  localStorage.removeItem('going')
  window.location.hash = '/akcia/' + id
}, eventId)
await sleep(1500)

await page.screenshot({
  path: path.join(OUT, '01-akcia-cena-idem.jpg'),
  type: 'jpeg',
  quality: 80,
})
console.log('01 done')

// --- Screenshot 2: Idem on (click Idem button) ---
await page.evaluate(() => {
  // find the round 40px idem button by aria-label
  const btns = Array.from(document.querySelectorAll('button'))
  const btn = btns.find(b => b.getAttribute('aria-label') === 'Pridané do Idem')
  if (btn) btn.click()
  else console.log('Idem button not found, labels:', btns.map(b => b.getAttribute('aria-label')).filter(Boolean).join(', '))
})
await sleep(600)

await page.screenshot({
  path: path.join(OUT, '02-akcia-vypredane-idem-zapnute.jpg'),
  type: 'jpeg',
  quality: 80,
})
console.log('02 done')

await browser.close()
console.log('All screenshots done.')
