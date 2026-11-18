import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

// Task 064 part 3: how the cancelled Omah Lay concert (Forum Karlín, 18. 11.)
// shows in the app with the real local site/events.json.
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/064')
fs.mkdirSync(OUT_DIR, { recursive: true })
const DATA = fs.readFileSync(path.resolve('D:/AI/eventapp/site/events.json'), 'utf-8')
const EVENT_ID = 'forum-karlin-2026-11-18-omah-lay'

test.describe('064', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 })
  test('omah-lay', async ({ page }) => {
    await page.clock.setFixedTime('2026-11-18T12:00:00')
    await page.addInitScript(() => { localStorage.setItem('language', 'sk') })
    await page.route('**/events.json', (route: any) =>
      route.fulfill({ contentType: 'application/json', body: DATA }))
    await page.goto(`/#/akcia/${EVENT_ID}`)
    await page.waitForSelector('text=Zdieľať', { timeout: 15000 })
    await page.waitForTimeout(1500)
    await page.screenshot({ path: path.join(OUT_DIR, 'omah-lay.jpg'), type: 'jpeg', quality: 80 })
  })
})
