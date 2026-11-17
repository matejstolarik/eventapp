// Task 055: verify the "new version" card with a real service worker.
// Needs a production build served by `vite preview` (run from web/):
//   npm run build
//   npx vite preview --port 4173 --strictPort
//   npx playwright test update-055 --reporter=dot
// The test simulates deploying version B by editing web/dist in place
// (marker in index.html + new precache revision in sw.js), then restores it.
import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const BASE = 'http://localhost:4173/eventapp/'
const DIST = path.resolve('D:/AI/eventapp/web/dist')
const OUT_DIR = path.resolve('D:/AI/eventapp/docs/tasks/055')
const EVENTS = path.resolve('D:/AI/eventapp/site/events.json')
const MARKER = '<meta name="test-build" content="B">'

test.describe('055', () => {
  test.use({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, serviceWorkers: 'allow' })

  test('update prompt A -> B', async ({ page, context }) => {
    fs.mkdirSync(OUT_DIR, { recursive: true })
    const indexPath = path.join(DIST, 'index.html')
    const swPath = path.join(DIST, 'sw.js')
    const indexA = fs.readFileSync(indexPath, 'utf-8')
    const swA = fs.readFileSync(swPath, 'utf-8')

    // events.json is not part of dist; serve the latest pipeline output (also via SW fetches).
    await context.route('**/events.json', route =>
      route.fulfill({ contentType: 'application/json', body: fs.readFileSync(EVENTS) }))
    await page.addInitScript(() => localStorage.setItem('language', 'sk'))

    try {
      // Version A: open and wait until the SW controls the page.
      await page.goto(BASE)
      await page.evaluate(async () => { await navigator.serviceWorker.ready })
      await page.reload()
      await page.waitForFunction(() => !!navigator.serviceWorker.controller)
      expect(await page.locator('meta[name="test-build"]').count()).toBe(0)
      await expect(page.getByText('Je dostupná nová verzia')).toHaveCount(0)

      // Deploy version B.
      fs.writeFileSync(indexPath, indexA.replace('</head>', `${MARKER}</head>`))
      const swB = swA.replace(/("index\.html",revision:")([0-9a-f]+)"/, '$1b055b055"')
      expect(swB).not.toBe(swA)
      fs.writeFileSync(swPath, swB)

      // Return to the app -> update check -> card.
      await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')))
      const card = page.getByText('Je dostupná nová verzia')
      await expect(card).toBeVisible({ timeout: 15000 })
      await page.waitForTimeout(400)
      await page.screenshot({ path: path.join(OUT_DIR, 'karta-nova-verzia.jpg'), type: 'jpeg', quality: 80 })

      // Close -> hidden; next return -> shown again.
      await page.getByRole('button', { name: 'Zavrieť' }).click()
      await expect(card).toHaveCount(0)
      await page.evaluate(() => document.dispatchEvent(new Event('visibilitychange')))
      await expect(card).toBeVisible()

      // Update -> reload into B.
      await Promise.all([
        page.waitForEvent('load', { timeout: 15000 }),
        page.getByRole('button', { name: 'Aktualizovať' }).click(),
      ])
      await expect(page.locator('meta[name="test-build"]')).toHaveCount(1)
      await expect(card).toHaveCount(0)
      console.log('OK: card shown, dismissed, re-shown, update reloaded into B')
    } finally {
      fs.writeFileSync(indexPath, indexA)
      fs.writeFileSync(swPath, swA)
    }
  })
})
