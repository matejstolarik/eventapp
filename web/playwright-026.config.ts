import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: '../tests/playwright',
  testMatch: 'screenshots-026.spec.ts',
  outputDir: '../docs/tasks/026/pw-output',
  use: {
    baseURL: 'http://localhost:5173/eventapp/',
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
  },
  projects: [
    {
      name: 'chromium-mobile',
      use: { ...devices['Pixel 5'] }
    }
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173/eventapp/',
    cwd: '.',
    reuseExistingServer: !process.env.CI,
    timeout: 60000
  }
})
