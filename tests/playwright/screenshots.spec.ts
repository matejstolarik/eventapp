import { test, expect } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT = path.resolve(__dirname, '../../docs/tasks/023')

async function screenshot(page: Parameters<typeof test.fn>[0]['page'], name: string) {
  const buf = await page.screenshot({ fullPage: false })
  fs.writeFileSync(path.join(OUT, `${name}.png`), buf)
}

test.describe('App screenshots 390x844', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('01-mapa', async ({ page }) => {
    await page.goto('/')
    // Wait for map to load
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2000)
    await screenshot(page, '01-mapa')
  })

  test('02-mapa-panel', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2000)
    // Click on first pill marker
    const marker = page.locator('.pill-marker').first()
    if (await marker.count() > 0) {
      await marker.click()
      await page.waitForTimeout(500)
    }
    await screenshot(page, '02-mapa-panel')
  })

  test('03-mapa-panel-viac', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2000)
    // Try to find a marker with +N badge
    const badge = page.locator('.pill-extra').first()
    if (await badge.count() > 0) {
      const marker = badge.locator('xpath=ancestor::div[contains(@class,"pill-marker")]')
      await marker.click()
    } else {
      const marker = page.locator('.pill-marker').first()
      if (await marker.count() > 0) await marker.click()
    }
    await page.waitForTimeout(500)
    await screenshot(page, '03-mapa-panel-viac')
  })

  test('04-vyber-dna', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(1000)
    // Click day selector button
    await page.getByRole('button', { name: /Dnes|Dnes|Today/i }).first().click()
    await page.waitForTimeout(300)
    await screenshot(page, '04-vyber-dna')
  })

  test('05-stranka-akcie-s-obrazkom', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 15000 })
    await page.waitForTimeout(2000)
    const marker = page.locator('.pill-marker').first()
    if (await marker.count() > 0) {
      await marker.click()
      await page.waitForTimeout(400)
      // Click on panel to open event page
      await page.locator('section[aria-label="Vybraná akcia"] button').click()
      await page.waitForTimeout(500)
    }
    await screenshot(page, '05-stranka-akcie-s-obrazkom')
  })

  test('06-stranka-akcie-bez-obrazka', async ({ page }) => {
    // Find an event without image_url via hash routing
    // Load events.json and find an event without image
    const eventsResp = await page.goto('/events.json')
    if (!eventsResp) return
    const data = await eventsResp.json()
    const noImg = (data as { events: Array<{ id: string; image_url: null | string }> })
      .events.find(e => !e.image_url)
    if (!noImg) return

    await page.goto(`/#/akcia/${noImg.id}`)
    await page.waitForTimeout(500)
    await screenshot(page, '06-stranka-akcie-bez-obrazka')
  })
})
