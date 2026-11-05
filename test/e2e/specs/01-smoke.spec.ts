import { test } from '../helpers/fixtures'
import { shoot } from '../helpers/screenshot'
import { env } from '../helpers/env'
import { login, addPerson } from '../helpers/gramps'

const user = env('PLAYWRIGHT_DEVICE_USER')
const password = env('PLAYWRIGHT_DEVICE_PASSWORD')

test('login and add a person', async ({ page }) => {
  await test.step('login', async () => {
    await login(page, user, password)
    await shoot(page, 'main')
  })
  await test.step('add person', async () => {
    await addPerson(page, 'Smoke', 'Person')
    await shoot(page, 'person-added')
  })
})
