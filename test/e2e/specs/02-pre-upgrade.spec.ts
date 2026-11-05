import { test } from '../helpers/fixtures'
import { shoot } from '../helpers/screenshot'
import { env } from '../helpers/env'
import { login, addPerson } from '../helpers/gramps'

const user = env('PLAYWRIGHT_DEVICE_USER')
const password = env('PLAYWRIGHT_DEVICE_PASSWORD')

test('add a person on the released version', async ({ page }) => {
  await login(page, user, password)
  await shoot(page, 'main-before-upgrade')
  await addPerson(page, 'Upgrade', 'Survivor')
  await shoot(page, 'person-before-upgrade')
})
