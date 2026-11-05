import { Locator, Page, expect } from '@playwright/test'

function item(parent: Locator, href: string): Locator {
  return parent.locator(`md-list-item[href='${href}']`)
    .or(parent.locator(`md-menu-item[href='${href}']`))
    .or(parent.locator(`grampsjs-list-item[href='${href}']`))
}

export async function login(page: Page, user: string, password: string) {
  await page.goto('/')
  await page.getByLabel('Username').fill(user)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: /^login$/i }).click()
  await expect(item(page.locator('grampsjs-main-menu'), '/')).toBeVisible()
}

export async function addPerson(page: Page, firstName: string, surname: string) {
  await page.locator('#button_add').or(page.locator('grampsjs-add-menu mwc-icon-button')).click()
  await item(page.locator('grampsjs-add-menu'), '/new_person').click()
  const form = page.locator('grampsjs-view-new-person')
  await expect(form.getByRole('heading', { name: 'New Person' })).toBeVisible()
  await form.getByLabel('Given name').fill(firstName)
  await form.getByLabel('Surname', { exact: true }).fill(surname)
  await form.locator('md-filled-button', { hasText: 'Add' }).or(form.locator('mwc-button[icon=save]')).click()
  await expect(page.locator('grampsjs-view-person').getByRole('heading', { name: `${firstName} ${surname}` })).toBeVisible()
}

export async function expectPerson(page: Page, firstName: string, surname: string) {
  await item(page.locator('grampsjs-main-menu'), '/people').click()
  const people = page.locator('grampsjs-view-people')
  await expect(people.getByText(firstName, { exact: true }).first()).toBeVisible()
  await expect(people.getByText(surname, { exact: true }).first()).toBeVisible()
}
