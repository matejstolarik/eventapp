import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT = path.resolve(__dirname, '../../docs/tasks/024')

async function screenshot(page: Parameters<typeof test.fn>[0]['page'], name: string) {
  const buf = await page.screenshot({ fullPage: false })
  fs.writeFileSync(path.join(OUT, `${name}.png`), buf)
}

test.describe('App screenshots 390x844 – task 024', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('01-mapa', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(3000)
    await screenshot(page, '01-mapa')
  })

  test('02-mapa-panel', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(3000)
    const marker = page.locator('.pill-marker').first()
    if (await marker.count() > 0) {
      await marker.click()
      await page.waitForTimeout(600)
    }
    await screenshot(page, '02-mapa-panel')
  })

  test('03-mapa-panel-viac', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(3000)
    const badge = page.locator('.pill-extra').first()
    if (await badge.count() > 0) {
      const marker = badge.locator('xpath=ancestor::div[contains(@class,"pill-marker")]')
      await marker.click()
    } else {
      const marker = page.locator('.pill-marker').first()
      if (await marker.count() > 0) await marker.click()
    }
    await page.waitForTimeout(600)
    await screenshot(page, '03-mapa-panel-viac')
  })

  test('04-vyber-dna', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(1500)
    // Day selector button contains day label text
    const dayBtn = page.locator('button').filter({ hasText: /Dnes|Today|Dnes|Mo|Tu|We|Th|Fr|Sa|Su/i }).first()
    await dayBtn.click()
    await page.waitForTimeout(400)
    await screenshot(page, '04-vyber-dna')
  })

  test('05-stranka-akcie', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(3000)
    const marker = page.locator('.pill-marker').first()
    if (await marker.count() > 0) {
      await marker.click()
      await page.waitForTimeout(500)
      const panelBtn = page.locator('section').first().locator('button').first()
      if (await panelBtn.count() > 0) {
        await panelBtn.click()
        await page.waitForTimeout(500)
      }
    }
    await screenshot(page, '05-stranka-akcie')
  })

  test('06-muj-ucet', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(1000)
    await page.getByRole('button', { name: /Môj účet|Můj účet|My account/i }).click()
    await page.waitForTimeout(400)
    await screenshot(page, '06-muj-ucet')
  })
})
