import { test } from '@playwright/test'
import path from 'path'
import fs from 'fs'

const OUT = path.resolve(__dirname, '../../docs/tasks/026')

async function screenshot(page: Parameters<typeof test.fn>[0]['page'], name: string) {
  const buf = await page.screenshot({ fullPage: false })
  fs.mkdirSync(OUT, { recursive: true })
  fs.writeFileSync(path.join(OUT, `${name}.png`), buf)
}

test.describe('App screenshots 390x844 – task 026', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('01-mapa-celkova', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(4000)
    // Zoom out to show wider Prague area
    for (let i = 0; i < 3; i++) {
      await page.keyboard.press('-')
      await page.waitForTimeout(300)
    }
    await page.waitForTimeout(1000)
    await screenshot(page, '01-mapa-celkova')
  })

  test('02-mapa-piny', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(4000)
    await screenshot(page, '02-mapa-piny')
  })

  test('03-mapa-vybrany-pin', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(4000)
    const pin = page.locator('.map-pin').first()
    if (await pin.count() > 0) {
      await pin.click()
      await page.waitForTimeout(800)
    }
    await screenshot(page, '03-mapa-vybrany-pin')
  })

  test('04-mapa-sipka-smer', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(4000)
    // Click first pin to open card
    const pin = page.locator('.map-pin').first()
    if (await pin.count() > 0) {
      await pin.click()
      await page.waitForTimeout(800)
      // Click east arrow (›) if visible
      const eastArrow = page.locator('button[aria-label="Východný"]')
      if (await eastArrow.count() > 0) {
        await eastArrow.click()
        await page.waitForTimeout(600)
      }
    }
    await screenshot(page, '04-mapa-sipka-smer')
  })

  test('05-stranka-akcie', async ({ page }) => {
    await page.goto('/')
    await page.waitForSelector('.maplibregl-canvas', { timeout: 20000 })
    await page.waitForTimeout(4000)
    const pin = page.locator('.map-pin').first()
    if (await pin.count() > 0) {
      await pin.click()
      await page.waitForTimeout(500)
      const panelBtn = page.locator('section').first().locator('button').first()
      if (await panelBtn.count() > 0) {
        await panelBtn.click()
        await page.waitForTimeout(500)
      }
    }
    await screenshot(page, '05-stranka-akcie')
  })
})
