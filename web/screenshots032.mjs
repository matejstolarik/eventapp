import { chromium } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const BASE = 'http://localhost:5175/eventapp/'
const OUT = 'D:\\AI\\eventapp\\docs\\tasks\\032'

fs.mkdirSync(OUT, { recursive: true })

const browser = await chromium.launch({ headless: true })

async function makeCtx(width = 390) {
  const ctx = await browser.newContext({
    viewport: { width, height: 844 },
    deviceScaleFactor: 2,
  })
  await ctx.addInitScript(() => { localStorage.setItem('language', 'sk') })
  return ctx
}

const ctx = await makeCtx(390)
const page = await ctx.newPage()

async function shot(hash, file, waitMs = 2500) {
  await page.goto(BASE + hash)
  await page.waitForTimeout(waitMs)
  await page.screenshot({ path: path.join(OUT, file) })
  console.log('saved', file)
}

// Get events data
const resp = await page.goto(BASE + 'events.json')
const data = await resp.json()
const eventWithArtist = data.events.find(e => e.artists?.length > 0) ?? data.events[0]
const eventWithPrice = data.events.find(e => e.price_text || e.free) ?? data.events[0]
const venue0 = data.venues[0]
// Find venue with most upcoming events
const venueCounts = {}
data.events.forEach(e => { venueCounts[e.venue_id] = (venueCounts[e.venue_id] || 0) + 1 })
const busyVenueId = Object.entries(venueCounts).sort((a,b) => b[1]-a[1])[0][0]

console.log('eventWithArtist:', eventWithArtist.id)
console.log('eventWithPrice:', eventWithPrice.id)
console.log('venue0:', venue0.id)
console.log('busyVenue:', busyVenueId)

// 1. Event page – Spotify + Navigate buttons, with artist event
await shot(`#/akcia/${eventWithArtist.id}`, '01-event-buttons.png')

// 2. Event page – with price (may differ from artist event)
if (eventWithPrice.id !== eventWithArtist.id) {
  await shot(`#/akcia/${eventWithPrice.id}`, '02-event-price.png')
}

// 3. Same at 360px
await ctx.close()
const ctx360 = await makeCtx(360)
const p360 = await ctx360.newPage()
await p360.goto(BASE + `#/akcia/${eventWithArtist.id}`)
await p360.waitForTimeout(2500)
await p360.screenshot({ path: path.join(OUT, '03-event-360px.png') })
console.log('saved 03-event-360px.png')
await ctx360.close()

const ctx2 = await makeCtx(390)
const p2 = await ctx2.newPage()

// 4. Venue profile – default (no favourite)
await p2.goto(BASE + `#/miesto/${venue0.id}`)
await p2.waitForTimeout(2500)
await p2.screenshot({ path: path.join(OUT, '04-venue-profile.png') })
console.log('saved 04-venue-profile.png')

// 5. Venue profile – with favourite active
await p2.evaluate((vid) => {
  const favs = JSON.parse(localStorage.getItem('favorites') || '[]')
  if (!favs.includes(vid)) favs.push(vid)
  localStorage.setItem('favorites', JSON.stringify(favs))
}, venue0.id)
await p2.reload()
await p2.waitForTimeout(2500)
await p2.screenshot({ path: path.join(OUT, '05-venue-heart-active.png') })
console.log('saved 05-venue-heart-active.png')

// 6. Busy venue (more events = likely multiple per day)
if (busyVenueId !== venue0.id) {
  await p2.goto(BASE + `#/miesto/${busyVenueId}`)
  await p2.waitForTimeout(2500)
  await p2.screenshot({ path: path.join(OUT, '06-venue-busy.png') })
  console.log('saved 06-venue-busy.png')
}

// 7. Places list
await p2.goto(BASE + '#/miesta')
await p2.waitForTimeout(2000)
await p2.screenshot({ path: path.join(OUT, '07-places-list.png') })
console.log('saved 07-places-list.png')

// 8. My Account – add some going events first
await p2.evaluate((ids) => {
  localStorage.setItem('going', JSON.stringify(ids))
}, data.events.slice(0, 3).map(e => e.id))
await p2.goto(BASE)
await p2.waitForTimeout(2000)
// Click Môj účet tab
await p2.evaluate(() => {
  const btns = Array.from(document.querySelectorAll('button'))
  const acc = btns.find(b => b.getAttribute('aria-label') === 'Môj účet' || b.textContent?.includes('čet'))
  acc?.click()
})
await p2.waitForTimeout(800)
await p2.screenshot({ path: path.join(OUT, '08-my-account.png') })
console.log('saved 08-my-account.png')

// 9. Map base (open panel on a venue)
await p2.goto(BASE)
await p2.waitForTimeout(4000)
await p2.screenshot({ path: path.join(OUT, '09-map-base.png') })
console.log('saved 09-map-base.png')

await ctx2.close()
await browser.close()
console.log('All done. Screenshots in', OUT)
