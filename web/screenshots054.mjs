/**
 * Task 054 screenshot: event page with a price and a description from AI.
 * Run from web/: node screenshots054.mjs <events.json> <event id>
 * Starts its own Vite dev server on port 5179 and stops it at the end.
 * events.json = the published output of the latest pipeline run.
 */
import { chromium } from '@playwright/test'
import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'

const [, , eventsPath, eventId] = process.argv
const PORT = 5179
const BASE = `http://localhost:${PORT}/eventapp/`
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\054'
fs.mkdirSync(OUT, { recursive: true })
const DATA = fs.readFileSync(eventsPath, 'utf-8')
const ev = JSON.parse(DATA).events.find(e => e.id === eventId)
if (!ev) throw new Error('event not found: ' + eventId)
const FROZEN = ev.date + 'T12:00:00'

const server = spawn('npx', ['vite', '--port', String(PORT), '--strictPort'], { shell: true, stdio: 'ignore' })
async function waitForServer() {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(BASE); if (r.ok) return } catch { /* not yet */ }
    await new Promise(r => setTimeout(r, 1000))
  }
  throw new Error('dev server did not start')
}

try {
  await waitForServer()
  const browser = await chromium.launch({ headless: true })
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })
  await ctx.addInitScript((iso) => {
    localStorage.setItem('language', 'sk')
    const fixed = new Date(iso).getTime()
    const RealDate = Date
    // eslint-disable-next-line no-global-assign
    Date = class extends RealDate {
      constructor(...a) { super(...(a.length ? a : [fixed])) }
      static now() { return fixed }
    }
  }, FROZEN)
  await ctx.route('**/events.json', route => route.fulfill({ contentType: 'application/json', body: DATA }))
  // event images from venue sites are not needed for the layout check
  await ctx.route(/\.(jpg|jpeg|png|webp)(\?.*)?$/i, route => route.abort())
  const page = await ctx.newPage()
  await page.goto(BASE + '#/akcia/' + eventId)
  await page.waitForTimeout(2500)
  // scroll so that price row and description are visible
  await page.evaluate(() => {
    const p = [...document.querySelectorAll('p')].sort((a, b) => b.textContent.length - a.textContent.length)[0]
    if (p) p.scrollIntoView({ block: 'end' })
  })
  await page.waitForTimeout(500)
  const body = await page.evaluate(() => document.body.innerText)
  const desc = (ev.descriptions && (ev.descriptions.sk || ev.descriptions.cs)) || ''
  console.log('price shown:', body.includes(ev.price_text), '| AI description (sk) shown:',
    desc !== '' && body.includes(desc.slice(0, 40)))
  await page.screenshot({ path: path.join(OUT, 'stranka-akcie-ai-popis.jpg'), type: 'jpeg', quality: 80 })
  await browser.close()
  console.log('saved stranka-akcie-ai-popis.jpg')
} finally {
  server.kill()
  if (process.platform === 'win32') spawn('taskkill', ['/pid', String(server.pid), '/T', '/F'], { shell: true })
}
