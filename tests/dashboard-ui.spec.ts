import { expect, test } from '@playwright/test'

test.use({
  viewport: { width: 1920, height: 1080 },
})

const getDesktopGridColumnCount = async (page: import('@playwright/test').Page) => {
  return page.locator('main section.grid').evaluate((element) => {
    const template = window.getComputedStyle(element).gridTemplateColumns

    return template.split(' ').filter(Boolean).length
  })
}

test('renders the desktop dashboard in three columns', async ({ page }) => {
  await page.goto('http://localhost:5173')

  await expect(page.getByRole('heading', { name: 'Watchlist' })).toBeVisible()
  await expect
    .poll(async () => {
      return getDesktopGridColumnCount(page)
    })
    .toBe(3)

  await expect(page.getByLabel('Filter watchlist symbols')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Search' })).toBeHidden()
})

test('bootstraps market data instead of landing in an empty error state', async ({ page }) => {
  await page.goto('http://localhost:5173')

  await expect(page.getByRole('heading', { name: 'Watchlist' })).toBeVisible()
  await expect(page.getByText('No stocks in watchlist')).toBeHidden()
  await expect(page.getByText('0 symbols')).toBeHidden()
  await expect(page.getByText('Not Found')).toBeHidden()
  await expect(page.getByText('Awaiting symbol')).toBeHidden()
  await expect
    .poll(async () => {
      return page.locator('button[aria-label^="Remove "]').count()
    })
    .toBeGreaterThan(0)
  await expect(page.getByText('Loading chart...')).toBeHidden()
  await expect(page.getByText('Price history unavailable for AMZN yet.')).toBeVisible()
})
