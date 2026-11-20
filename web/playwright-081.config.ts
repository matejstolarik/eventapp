import { defineConfig, devices } from '@playwright/test'

// Task 081 smoothness measurement (production builds served by `vite preview`,
// see tests/playwright/perf-081.spec.ts). No dev server.
export default defineConfig({
  testDir: '../tests/playwright',
  testMatch: /(perf|navpill)-081.spec.ts/,
  outputDir: '../test-results/081',
  use: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 },
  projects: [{ name: 'chromium-mobile', use: { ...devices['Pixel 5'] } }],
})
