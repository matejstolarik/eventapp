import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 060 part 8: event detail with / without a verified Spotify link.
// Real local site/events.json; the Spotify link is a local test record
// (like a data/manual.json entry), never committed to the data.
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/060')
fs.mkdirSync(OUT_DIR, { recursive: true })
const DATA = JSON.parse(fs.readFileSync(path.resolve('D:/AI/eventapp/site/events.json'), 'utf-8'))
const EVENT_ID = 'kasarna-karlin-2026-12-02-bad-karma-boy-album-launch-island-mint'
const TEST_LINK = { name: 'Bad Karma Boy', spotify_url: 'https://open.spotify.com/artist/TESTTESTTESTTESTTESTTE' }

async function setup(page: any, withLink: boolean) {
  await page.clock.setFixedTime('2026-11-17T18:00:00')
  await page.addInitScript(() => { localStorage.setItem('language', 'sk') })
  const data = JSON.parse(JSON.stringify(DATA))
  for (const e of data.events) {
    if (e.id === EVENT_ID) e.artist_links = withLink ? [TEST_LINK] : null
  }
  await page.route('**/events.json', (route: any) =>
    route.fulfill({ contentType: 'application/json', body: JSON.stringify(data) }))
}

test.describe('060', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })
  for (const [name, withLink] of [['detail-spotify', true], ['detail-bez-spotify', false]] as const) {
    test(name, async ({ page }) => {
      await setup(page, withLink)
      await page.goto(`/#/akcia/${EVENT_ID}`)
      await page.waitForSelector('text=Zdieľať', { timeout: 15000 })
      await page.waitForTimeout(1200)
      await page.mouse.wheel(0, 380)
      await page.waitForTimeout(500)
      await page.screenshot({ path: path.join(OUT_DIR, `${name}.jpg`), type: 'jpeg', quality: 80 })
    })
  }
})
