import { test, expect } from '@playwright/test'

// Task 081 fix: the nav pill must move (transform transition), not jump.
// Run against `vite preview` of the current build on port 4181.
const BASE = process.env.AFTER_URL ?? 'http://localhost:4181/eventapp/'
const PAGES = 'https://matejstolarik.github.io/eventapp/'

test('nav pill moves with a transition', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('language', 'sk'); localStorage.setItem('onboardingDone', '1')
  })
  await page.route('**/events.json', async r => r.fulfill({ response: await r.fetch({ url: PAGES + 'events.json' }) }))
  await page.goto(BASE + '#/akcie')
  await page.waitForSelector('[data-testid="nav-pill"]')
  await page.waitForTimeout(1500)
  const xs = await page.evaluate(async () => {
    const pill = document.querySelector('[data-testid="nav-pill"]') as HTMLElement
    const x = () => new DOMMatrix(getComputedStyle(pill).transform).m41
    const start = x()
    ;(document.querySelector('nav button[aria-label="Miesta"]') as HTMLElement).click()
    const samples: number[] = []
    for (let i = 0; i < 20; i++) { await new Promise(r => requestAnimationFrame(r)); samples.push(Math.round(x())) }
    return { start: Math.round(start), samples }
  })
  console.log(JSON.stringify(xs))
  const end = xs.samples[xs.samples.length - 1]!
  const between = xs.samples.filter(v => v > Math.min(xs.start, end) + 2 && v < Math.max(xs.start, end) - 2)
  expect(between.length).toBeGreaterThan(3)
})
